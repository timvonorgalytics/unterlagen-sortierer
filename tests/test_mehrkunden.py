"""Mehrere Kunden in einem Durchlauf: Unterordner je Person (Ordner + ZIP) und
„Neue Dateien einlesen“ (erledigte Zeilen verschwinden, nur neue Dateien kommen dazu)."""
import asyncio, io, zipfile, subprocess, os, time
from playwright.async_api import async_playwright
from _gemeinsam import ROOT, DOCS_DIR, Pruefer

P = Pruefer("Mehrkunden")
PORT = 8766
URL = f"http://localhost:{PORT}/Unterlagen-Sortierer/app/index.html"
APP_FILE = (ROOT / "Unterlagen-Sortierer" / "app" / "index.html").as_uri()
MOCK = """window.showDirectoryPicker = async () => (await navigator.storage.getDirectory()).getDirectoryHandle('scans', { create: true });"""
LIST = """async () => { const w = async (d, pfx) => { const out = {};
  for await (const [n, h] of d.entries()) { if (h.kind === 'file') out[pfx + n] = (await h.getFile()).size;
    else Object.assign(out, await w(h, pfx + n + '/')); } return out; };
  return w(await (await navigator.storage.getDirectory()).getDirectoryHandle('scans'), ''); }"""

async def put(pg, names):
    await pg.evaluate("""async (docs) => { const root = await navigator.storage.getDirectory();
      const d = await root.getDirectoryHandle('scans', { create: true });
      for (const n of docs) { const b = await (await fetch('/tests/testdocs/' + n)).blob();
        const w = await (await d.getFileHandle(n, { create: true })).createWritable(); await w.write(b); await w.close(); } }""", names)

async def main():
    srv = subprocess.Popen(["python3", "-m", "http.server", str(PORT), "-d", str(ROOT)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)
    try:
        async with async_playwright() as p:
            b = await p.chromium.launch(); ctx = await b.new_context(accept_downloads=True); await ctx.add_init_script(MOCK)
            pg = await ctx.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.on("dialog", lambda d: asyncio.ensure_future(d.accept()))

            # A) Ordnermodus, Originale umbenennen, je Person ein Unterordner; zwei Personen im selben Ordner
            await pg.goto(URL)
            await pg.evaluate("async () => { const r = await navigator.storage.getDirectory(); try { await r.removeEntry('scans', { recursive: true }); } catch {} }")
            await put(pg, ["Scan_0002.pdf", "Scan_0004.pdf"])
            await pg.check("input[name=ablage][value=umbenennen]")
            await pg.check("#perperson")
            await pg.click("#pick")
            await pg.wait_for_function("state.items.length === 2 && !state.busy", timeout=240000)
            P.check("Knopf Neue Dateien sichtbar", await pg.is_visible("#rescan"))
            await pg.click("#apply"); await pg.wait_for_function("!state.busy")
            fs = await pg.evaluate(LIST)
            P.check("Erika-Unterordner", "Mustermann_Erika/Mustermann_Erika_Kontoauszug.pdf" in fs, list(fs))
            P.check("Hans-Unterordner", "Mustermann_Hans/Mustermann_Hans_Rentenbescheid.pdf" in fs, list(fs))
            P.check("Keine Originale mehr oben", "Scan_0002.pdf" not in fs and "Scan_0004.pdf" not in fs, list(fs))
            P.check("Protokoll im Hauptordner", any(k.startswith("Protokoll_") for k in fs), list(fs))

            # B) Neue Dateien einlesen: erledigte Zeilen fliegen raus, nur die neue Datei kommt dazu
            await put(pg, ["Scan_0005.pdf"])
            await pg.click("#rescan")
            await pg.wait_for_function("!state.busy && state.items.length === 1", timeout=240000)
            r = await pg.evaluate("state.items.map(i => ({ d: i.name, st: i.status }))")
            P.check("Nur die neue Datei in der Liste", len(r) == 1 and r[0]["d"] == "Scan_0005.pdf" and r[0]["st"] == "done", r)
            await pg.click("#rescan")
            await pg.wait_for_function("document.querySelector('#status').textContent.includes('Keine neuen Dateien')", timeout=15000)
            P.check("Meldung: keine neuen Dateien", True)
            P.check("Nichts doppelt eingelesen", await pg.evaluate("state.items.length") == 1)

            # B2) Stammordner: zugezogene Datei ERGÄNZT die Liste und wird beim Speichern in den Ordner übernommen
            await pg.evaluate("""async () => {
                const b = await (await fetch('/tests/testdocs/Scan_0002.pdf')).blob();
                const dt = new DataTransfer();
                dt.items.add(new File([b], 'Mail_Anhang.pdf', { type: 'application/pdf' }));
                window.dispatchEvent(new DragEvent('drop', { dataTransfer: dt, cancelable: true }));
            }""")
            await pg.wait_for_function("state.items.length === 2 && !state.busy", timeout=240000)
            P.check("Stammordner bleibt verbunden", await pg.evaluate("state.dir !== null"))
            r = await pg.evaluate("state.items.map(i => ({ d: i.name, ex: !!i.extern }))")
            P.check("Zugezogene Datei ergänzt", any(x["d"] == "Mail_Anhang.pdf" and x["ex"] for x in r), r)
            await pg.click("#apply"); await pg.wait_for_function("!state.busy")
            fs = await pg.evaluate(LIST)
            P.check("Externe Datei im Stammordner", "Mustermann_Erika/Mustermann_Erika_Kontoauszug.pdf" in fs, list(fs))
            P.check("Scan_0005 verarbeitet", any("Krankenversicherung" in k for k in fs), list(fs))
            logs = sorted(k for k in fs if k.startswith("Protokoll_"))
            logtxt = await pg.evaluate("""async (n) => { const d = await (await navigator.storage.getDirectory()).getDirectoryHandle('scans');
                return await (await (await d.getFileHandle(n)).getFile()).text(); }""", logs[-1])
            P.check("Hinweis im Protokoll", "Per Drag & Drop hinzugefügt" in logtxt)

            # C) Dateimodus (ZIP): Unterordner je Person als Pfade im ZIP
            await pg.goto(APP_FILE)
            await pg.check("#perperson")
            await pg.set_input_files("#filepick", [str(DOCS_DIR / "Scan_0002.pdf"), str(DOCS_DIR / "Scan_0004.pdf")])
            await pg.wait_for_function("state.items.length === 2 && !state.busy", timeout=240000)
            async with pg.expect_download() as dl:
                await pg.click("#apply")
            z = zipfile.ZipFile(io.BytesIO(open(await (await dl.value).path(), "rb").read()))
            names = z.namelist()
            P.check("ZIP mit Personen-Pfaden", "Mustermann_Erika/Mustermann_Erika_Kontoauszug.pdf" in names
                    and "Mustermann_Hans/Mustermann_Hans_Rentenbescheid.pdf" in names, names)
            log = z.read([x for x in names if x.startswith("Protokoll")][0]).decode("utf-8-sig")
            P.check("Pfad im Protokoll", "Mustermann_Erika/Mustermann_Erika_Kontoauszug.pdf" in log)
            P.check("Keine JS-Fehler", not errs, errs[:3])
            await b.close()
    finally:
        srv.terminate()
    P.ende()

asyncio.run(main())
