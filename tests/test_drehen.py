"""Drehen und Anzeigen: automatische Dreh-Erkennung (OCR), Drehen von Hand,
gedrehtes Speichern, Vorschau im Ordnermodus, Zoom im Teilen-Dialog."""
import asyncio, io, zipfile
from playwright.async_api import async_playwright
from pypdf import PdfReader
from _gemeinsam import APP, DOCS, DOCS_DIR, Pruefer
P = Pruefer("Drehen")
GEDREHT = str(DOCS_DIR / "extra" / "Scan_Gedreht.pdf")
def rotation(raw):
    return PdfReader(io.BytesIO(raw)).pages[0].get("/Rotate", 0)

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(accept_downloads=True, viewport={"width": 1440, "height": 1000})
        errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))

        # A) Automatische Dreh-Erkennung: um 90 Grad verdrehter Scan wird trotzdem erkannt
        await pg.goto(APP)
        await pg.set_input_files("#filepick", GEDREHT)
        await pg.wait_for_function("state.items.length && !state.busy", timeout=240000)
        it = await pg.evaluate("({t: state.items[0].type, n: state.items[0].nachname + ' ' + state.items[0].vorname, rot: (state.items[0].pageRot||[])[0]})")
        P.check("Verdrehter Scan: Typ erkannt", it["t"] == "Mietbescheinigung", it)
        P.check("Verdrehter Scan: Name erkannt", it["n"] == "Mustermann Erika", it)
        P.check("Drehung erkannt (90/270)", it["rot"] in (90, 270), it)
        thumb = await pg.evaluate("state.items[0].thumb")
        import base64
        from PIL import Image
        im = Image.open(io.BytesIO(base64.b64decode(thumb.split(",", 1)[1])))
        P.check("Miniatur steht aufrecht (Hochformat)", im.height > im.width, im.size)

        # Beim Speichern (ZIP-Weg) wird die Drehung in die Kopie geschrieben
        async with pg.expect_download() as dl:
            await pg.click("#apply")
        z = zipfile.ZipFile(io.BytesIO(open(await (await dl.value).path(), "rb").read()))
        name = [n for n in z.namelist() if n.endswith(".pdf")][0]
        raw = z.read(name)
        P.check("Kopie heißt nach Person und Typ", "Mustermann_Erika_Mietbescheinigung" in name, name)
        P.check("Drehung in der PDF gespeichert", rotation(raw) in (90, 270), rotation(raw))
        log = z.read([n for n in z.namelist() if n.startswith("Protokoll")][0]).decode("utf-8-sig")
        P.check("Protokoll-Hinweis aufs Drehen", "gerade gedreht" in log)

        # B) Drehen von Hand in der Vorschau (gerades Dokument)
        await pg.goto(APP)
        await pg.set_input_files("#filepick", str(DOCS_DIR / "Rentenanpassung_digital.pdf"))
        await pg.wait_for_function("state.items.length && !state.busy", timeout=240000)
        await pg.click("button.thumbbox")
        await pg.wait_for_function("document.querySelector('#pvpage').textContent.includes('Seite 1')", timeout=60000)
        await pg.click("#pvrot")
        P.check("Vorschau-Drehen setzt pageRot", await pg.evaluate("(state.items[0].pageRot||[])[0]") == 90)
        await pg.click("#pvclose")
        async with pg.expect_download() as dl:
            await pg.click("#apply")
        z = zipfile.ZipFile(io.BytesIO(open(await (await dl.value).path(), "rb").read()))
        raw = z.read([n for n in z.namelist() if n.endswith(".pdf")][0])
        P.check("Hand-Drehung in der PDF gespeichert", rotation(raw) == 90, rotation(raw))

        # C) Vorschau im Ordnermodus (Datei nur mit handle, ohne file-Objekt)
        await pg.goto(APP)
        await pg.set_input_files("#filepick", DOCS)
        await pg.wait_for_function("state.items.length && !state.busy", timeout=240000)
        r = await pg.evaluate("""(async () => {
          const it = state.items.find(i => /jpg$/i.test(i.name));
          const f = it.file; it.handle = { getFile: async () => f }; delete it.file;
          await openPreview(it);
          await new Promise(r => setTimeout(r, 400));
          return { seite: document.querySelector('#pvpage').textContent,
                   hatBild: !!document.querySelector('#pvimg').src };
        })()""")
        P.check("Bildvorschau im Ordnermodus zeigt das Bild", r["hatBild"] and "nicht möglich" not in r["seite"], r)
        await pg.evaluate("closePreview()")

        # D) Zoom liegt IM Teilen-Dialog und damit sichtbar über ihm; Esc schließt erst den Zoom
        P.check("Zoom-Element liegt im Dialog", await pg.evaluate("!!document.querySelector('#splitdlg #zoom')"))
        await pg.click("button.split")
        await pg.wait_for_function("!split.running && split.pages.length === 5", timeout=240000)
        await pg.click("#splitpages .page img >> nth=0")
        await pg.wait_for_function("!document.querySelector('#zoom').classList.contains('hidden')")
        mitte = await pg.evaluate("(() => { const el = document.elementFromPoint(720, 500); return el ? (el.id || el.tagName) : ''; })()")
        P.check("Vergrößerte Seite liegt oben", mitte == "zoomimg", mitte)
        await pg.keyboard.press("Escape")
        P.check("Esc schließt nur den Zoom", await pg.evaluate("document.querySelector('#zoom').classList.contains('hidden') && document.querySelector('#splitdlg').open"))
        P.check("Drehen-Knopf an jeder Seite", await pg.evaluate("document.querySelectorAll('#splitpages .rotpage').length") == 5)

        # E) Teilen/Zusammenführen: keine doppelte Hintergrund-Lesung, kein Text-Versatz
        await pg.evaluate("document.querySelector('#splitok').click()")
        await pg.wait_for_function("state.items.some(i => i.derived)", timeout=240000)
        ok = await pg.evaluate("state.items.filter(i => i.derived).every(i => i.pagesRead === i.pages && (i.pageTexts||[]).length === i.pages)")
        P.check("Geteilte Dateien gelten als fertig gelesen", ok)
        # Zusammenführen mit einer absichtlich teilgelesenen Quelle
        pg.on("dialog", lambda d: asyncio.ensure_future(d.accept()))
        await pg.evaluate("""(() => {
          state.items.forEach(i => i.selected = false);
          const a = state.items[0], b = state.items[1];
          a.selected = true; b.selected = true;
          b.pagesRead = 0; b.pageTexts = [];   // Quelle gilt als nicht fertig gelesen
          b.pages = 2;
        })()""")
        await pg.evaluate("mergeSelected()")
        await pg.wait_for_function("state.items.some(i => (i.name||'').includes('_gesamt'))", timeout=240000)
        g = await pg.evaluate("(() => { const i = state.items.find(x => x.name.includes('_gesamt')); return { pt: (i.pageTexts||[]).length, pr: i.pagesRead }; })()")
        P.check("Merge übernimmt keine verrutschten Seitentexte", g["pt"] == 0 and g["pr"] == 0, g)

        P.check("Keine JS-Fehler", not errs, errs[:3])
        await b.close()
    P.ende()
asyncio.run(main())
