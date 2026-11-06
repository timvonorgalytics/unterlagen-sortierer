"""Standard-Ablage im Ordnermodus (File System Access API): Kopien nach umbenannt/<Person>/,
Originale nach verarbeitet/, Ersatzweg ohne move(), keine Überschreibung, Fremddateien,
Neustart liest nichts doppelt. Der Ordner-Dialog wird durch das private Dateisystem des
Browsers (OPFS) ersetzt; dafür läuft ein lokaler Webserver."""
import asyncio, subprocess, os, time
from playwright.async_api import async_playwright
from _gemeinsam import ROOT, DOCS, DOCS_DIR, Pruefer

PORT = 8765
NAMES = [os.path.basename(d) for d in DOCS]
URL = f"http://localhost:{PORT}/Unterlagen-Sortierer/Unterlagen-Sortierer.html"
MOCK = """window.showDirectoryPicker = async () => (await navigator.storage.getDirectory()).getDirectoryHandle('scans', { create: true });"""
LIST = """async () => { const w = async (d, pfx) => { const out = {};
  for await (const [n, h] of d.entries()) { if (h.kind === 'file') out[pfx + n] = (await h.getFile()).size;
    else Object.assign(out, await w(h, pfx + n + '/')); } return out; };
  return w(await (await navigator.storage.getDirectory()).getDirectoryHandle('scans'), ''); }"""
P = Pruefer("Ordnermodus")

async def fresh(pg, nomove=False):
    await pg.goto(URL)
    await pg.evaluate("""async (docs) => { const root = await navigator.storage.getDirectory();
      try { await root.removeEntry('scans', { recursive: true }); } catch {}
      const d = await root.getDirectoryHandle('scans', { create: true });
      for (const n of docs) { const b = await (await fetch('/tests/testdocs/' + n)).blob(); const w = await (await d.getFileHandle(n, {create:true})).createWritable(); await w.write(b); await w.close(); }
      const w = await (await d.getFileHandle('notizen.txt', {create:true})).createWritable(); await w.write('x'); await w.close(); }""", NAMES)
    if nomove: await pg.evaluate("FileSystemFileHandle.prototype.move = undefined")
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
            # Standard-Ablage: Kopien je Person, Originale nach verarbeitet
            await fresh(pg)
            P.check("Nur PDF/JPG/PNG eingelesen", await pg.evaluate("state.items.length") == len(NAMES))
            P.check("Knopf: Kopien", await pg.inner_text("#apply") == "Umbenannte Kopien speichern")
            await pg.click("#apply"); await pg.wait_for_function("!state.busy")
            fs = await pg.evaluate(LIST)
            kopien = [k for k in fs if k.startswith("umbenannt/") and not k.endswith(".csv")]
            P.check("Kopien je Person in umbenannt/", "umbenannt/Mustermann_Erika/Mustermann_Erika_Antrag.pdf" in fs
                    and "umbenannt/Mustermann_Hans/Mustermann_Hans_Rentenbescheid.pdf" in fs, sorted(fs))
            P.check("Alle Kopien da", len(kopien) == len(NAMES), kopien)
            P.check("Kopie vollständig", fs.get("umbenannt/Mustermann_Erika/Mustermann_Erika_Antrag.pdf") == size)
            P.check("Originale nach verarbeitet", all(f"verarbeitet/{n}" in fs for n in NAMES)
                    and not any(n in fs for n in NAMES), sorted(fs))
            P.check("Protokoll in umbenannt", any(k.startswith("umbenannt/Protokoll_") for k in fs))
            P.check("Fremddatei unberührt", "notizen.txt" in fs)
            # zweiter Lauf in denselben Unterordner → nichts überschreiben
            await pg.evaluate("state.items.forEach(i=>{ if(i.status==='applied'){ i.status='done'; i.name=i.originalName; } }); updateActions()")
            await pg.click("#apply"); await pg.wait_for_function("!state.busy")
            fs2 = await pg.evaluate(LIST)
            P.check("Nichts überschrieben (_2)", "umbenannt/Mustermann_Erika/Mustermann_Erika_Antrag_2.pdf" in fs2
                    and "umbenannt/Mustermann_Erika/Mustermann_Erika_Antrag.pdf" in fs2, sorted(fs2))
            # Browser "neu gestartet": Ordner erneut wählen → nichts mehr offen, nichts doppelt
            await pg.goto(URL)
            await pg.click("#pick")
            await pg.wait_for_function("document.querySelector('#status').textContent.includes('keine PDF')", timeout=30000)
            P.check("Nach Neustart nichts mehr offen", await pg.evaluate("state.items.length") == 0)
            # Ersatzweg ohne move(): Original wird kopiert + gelöscht
            await fresh(pg, nomove=True)
            await pg.click("#apply"); await pg.wait_for_function("!state.busy")
            fs3 = await pg.evaluate(LIST)
            P.check("Ersatzweg: Kopie da, Original in verarbeitet", "umbenannt/Mustermann_Erika/Mustermann_Erika_Antrag.pdf" in fs3
                    and "verarbeitet/Scan_0001.pdf" in fs3 and "Scan_0001.pdf" not in fs3, sorted(fs3))
            P.check("Ersatzweg vollständig", fs3.get("umbenannt/Mustermann_Erika/Mustermann_Erika_Antrag.pdf") == size)
            P.check("Keine JS-Fehler", not errs, errs[:3])
            await b.close()
    finally:
        srv.terminate()
    P.ende()
asyncio.run(main())
