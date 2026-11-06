"""Ordnerzugriff (File System Access API): Kopien, echtes Umbenennen, Ersatzweg ohne move(), keine Überschreibung.
Der Ordner-Dialog wird durch das private Dateisystem des Browsers (OPFS) ersetzt; dafür läuft ein lokaler Webserver."""
import asyncio, subprocess, os, time
from playwright.async_api import async_playwright
from _gemeinsam import ROOT, DOCS, DOCS_DIR, Pruefer

PORT = 8765
NAMES = [os.path.basename(d) for d in DOCS]
URL = f"http://localhost:{PORT}/Unterlagen-Sortierer/app/index.html"
MOCK = """window.showDirectoryPicker = async () => (await navigator.storage.getDirectory()).getDirectoryHandle('scans', { create: true });"""
LIST = """async () => { const d = await (await navigator.storage.getDirectory()).getDirectoryHandle('scans');
  const out = {}; for await (const [n,h] of d.entries()) { if (h.kind==='file') out[n]=(await h.getFile()).size;
    else { out[n+'/']={}; for await (const [m,g] of h.entries()) out[n+'/'][m]=(await g.getFile()).size; } } return out; }"""
P = Pruefer("Ordnermodus")

async def fresh(pg, nomove=False):
    await pg.goto(URL)
    await pg.evaluate("""async (docs) => { const root = await navigator.storage.getDirectory();
      try { await root.removeEntry('scans', { recursive: true }); } catch {}
      const d = await root.getDirectoryHandle('scans', { create: true });
      for (const n of docs) { const b = await (await fetch('/tests/testdocs/' + n)).blob(); const w = await (await d.getFileHandle(n, {create:true})).createWritable(); await w.write(b); await w.close(); }
      const w = await (await d.getFileHandle('notizen.txt', {create:true})).createWritable(); await w.write('x'); await w.close(); }""", NAMES)
    if nomove: await pg.evaluate("FileSystemFileHandle.prototype.move = undefined")
    await pg.fill("#vNach", "Mustermann"); await pg.fill("#vVor", "Erika")
    await pg.click("#pick")
    await pg.wait_for_function("state.items.length && !state.busy", timeout=240000)

async def main():
    srv = subprocess.Popen(["python3", "-m", "http.server", str(PORT), "-d", str(ROOT)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)
    try:
        async with async_playwright() as p:
            b = await p.chromium.launch(); ctx = await b.new_context(); await ctx.add_init_script(MOCK)
            pg = await ctx.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.on("dialog", lambda d: asyncio.ensure_future(d.accept()))
            size = os.path.getsize(DOCS_DIR / "Scan_0001.pdf")
            # Kopien
            await fresh(pg)
            P.check("Nur PDF/JPG/PNG eingelesen", await pg.evaluate("state.items.length") == len(NAMES))
            P.check("Knopf: Kopien", await pg.inner_text("#apply") == "Umbenannte Kopien speichern")
            await pg.click("#apply"); await pg.wait_for_function("!state.busy")
            fs = await pg.evaluate(LIST); sub = fs.get("umbenannt/", {}); verarb = fs.get("verarbeitet/", {})
            P.check("Originale nach verarbeitet verschoben", all(n in verarb for n in NAMES) and not any(n in fs for n in NAMES), list(fs))
            P.check("Kopien + Protokoll", len(sub) == len(NAMES) + 1, list(sub))
            P.check("Kopie vollständig", sub.get("Mustermann_Erika_Antrag.pdf") == size)
            # zweiter Lauf in denselben Unterordner
            await pg.evaluate("state.items.forEach(i=>{ if(i.status==='applied'){ i.status='done'; i.name=i.originalName; } }); updateActions()")
            await pg.click("#apply"); await pg.wait_for_function("!state.busy")
            sub2 = (await pg.evaluate(LIST)).get("umbenannt/", {})
            P.check("Nichts überschrieben (_2)", "Mustermann_Erika_Antrag_2.pdf" in sub2 and "Mustermann_Erika_Antrag.pdf" in sub2)
            # Browser "neu gestartet": Ordner erneut wählen -> nichts mehr offen, nichts doppelt
            await pg.goto(URL)
            await pg.click("#pick")
            await pg.wait_for_function("document.querySelector('#status').textContent.includes('keine PDF')", timeout=30000)
            P.check("Nach Neustart nichts mehr offen", await pg.evaluate("state.items.length") == 0)
            # Originale umbenennen
            await fresh(pg); await pg.check("input[name=ablage][value=umbenennen]")
            P.check("Knopf: Umbenennen", await pg.inner_text("#apply") == "Dateien umbenennen")
            await pg.click("#apply"); await pg.wait_for_function("!state.busy")
            fs = await pg.evaluate(LIST)
            P.check("Originalnamen weg", not any(n in fs for n in NAMES), list(fs))
            P.check("Neue Namen da", "Mustermann_Erika_Antrag.pdf" in fs)
            P.check("Fremddatei unberührt", "notizen.txt" in fs)
            P.check("Protokoll im Ordner", any(k.startswith("Protokoll_") for k in fs))
            # ohne move()
            await fresh(pg, nomove=True); await pg.check("input[name=ablage][value=umbenennen]")
            await pg.click("#apply"); await pg.wait_for_function("!state.busy")
            fs = await pg.evaluate(LIST)
            P.check("Ersatzweg kopiert + löscht", "Mustermann_Erika_Antrag.pdf" in fs and "Scan_0001.pdf" not in fs)
            P.check("Ersatzweg vollständig", fs.get("Mustermann_Erika_Antrag.pdf") == size)
            P.check("Keine JS-Fehler", not errs, errs[:3])
            await b.close()
    finally:
        srv.terminate()
    P.ende()
asyncio.run(main())
