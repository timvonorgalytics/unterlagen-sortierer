"""Teilen von Stapel-Scans (mehrere Dokumente in einer PDF) und Zusammenführen mehrerer Dateien."""
import asyncio, io, zipfile, base64
from playwright.async_api import async_playwright
from _gemeinsam import APP, DOCS_DIR, Pruefer

P = Pruefer("Teilen/Zusammenführen")
PAGECOUNT = """async (b64) => { const d = await pdfjsLib.getDocument({ data: Uint8Array.from(atob(b64), c => c.charCodeAt(0)) }).promise;
  const n = d.numPages; await d.destroy(); return n; }"""

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(accept_downloads=True, viewport={"width": 1440, "height": 1100})
        errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("dialog", lambda d: asyncio.ensure_future(d.accept()))

        # A) Stapel-Scan laden (alle Seiten auswerten, damit der Hinweis greift)
        await pg.goto(APP)
        await pg.select_option("#seiten", "5")
        await pg.set_input_files("#filepick", [str(DOCS_DIR / "Scan_0007_Stapel.pdf")])
        await pg.wait_for_function("state.items.length && !state.busy", timeout=240000)
        P.check("Mehrtyp-Hinweis", await pg.evaluate("state.items[0].multiHint === true"))
        P.check("Teilen-Knopf sichtbar", await pg.is_visible("button.split"))

        # B) Dialog: Seiten lesen, Vorschlag prüfen, Trennstelle von Hand ändern
        await pg.click("button.split")
        await pg.wait_for_function("!split.running && split.pages.length === 4", timeout=240000)
        cuts = await pg.evaluate("[...split.cuts].sort().join(',')")
        P.check("Trennstelle vor Seite 3 vorgeschlagen", cuts == "2", f"→ '{cuts}'")
        P.check("Knopf: In 2 Dateien teilen", await pg.inner_text("#splitok") == "In 2 Dateien teilen")
        await pg.click(".cut[data-i='1']")
        P.check("Von Hand: 3 Teile", await pg.inner_text("#splitok") == "In 3 Dateien teilen")
        await pg.click(".cut[data-i='1']")
        P.check("Wieder 2 Teile", await pg.inner_text("#splitok") == "In 2 Dateien teilen")

        # C) Teilen ausführen
        await pg.click("#splitok")
        await pg.wait_for_function("state.items.length === 3")
        rows = await pg.evaluate("state.items.map(i => ({ n: i.name, t: i.type, sel: i.selected, pg: i.pages, d: !!i.derived, nn: i.nachname + ' ' + i.vorname }))")
        P.check("Original abgewählt", rows[0]['sel'] is False and rows[0]['d'] is False, rows[0])
        P.check("Teil 1: Antrag, 2 Seiten", rows[1]['t'] == "Antrag" and rows[1]['pg'] == 2 and rows[1]['d'], rows[1])
        P.check("Teil 2: Kontoauszug, 2 Seiten", rows[2]['t'] == "Kontoauszug" and rows[2]['pg'] == 2 and rows[2]['d'], rows[2])
        P.check("Namen erkannt", rows[1]['nn'] == "Mustermann Erika" and rows[2]['nn'] == "Mustermann Erika", rows)

        # D) ZIP-Export: zwei neue PDFs mit je 2 Seiten + Protokoll mit Hinweis
        async with pg.expect_download() as dl:
            await pg.click("#apply")
        z = zipfile.ZipFile(io.BytesIO(open(await (await dl.value).path(), "rb").read()))
        names = z.namelist()
        P.check("2 Teile + Protokoll", len(names) == 3, names)
        P.check("Antrag-PDF im ZIP", "Mustermann_Erika_Antrag.pdf" in names, names)
        P.check("Kontoauszug-PDF im ZIP", "Mustermann_Erika_Kontoauszug.pdf" in names, names)
        teil = z.read("Mustermann_Erika_Antrag.pdf")
        P.check("Gültige PDF-Datei", teil[:5] == b"%PDF-")
        n = await pg.evaluate(PAGECOUNT, base64.b64encode(teil).decode())
        P.check("Teil hat 2 Seiten", n == 2, n)
        log = z.read([x for x in names if x.startswith("Protokoll")][0]).decode("utf-8-sig")
        P.check("Hinweis im Protokoll", "Seiten 1–2" in log and "Scan_0007_Stapel.pdf" in log)

        # E) Zusammenführen: PDF + Foto → eine PDF mit 2 Seiten
        await pg.goto(APP)
        await pg.set_input_files("#filepick", [str(DOCS_DIR / "Scan_0002.pdf"), str(DOCS_DIR / "Foto_Ausweis.jpg")])
        await pg.wait_for_function("state.items.length === 2 && !state.busy", timeout=240000)
        P.check("Zusammenführen sichtbar", await pg.is_visible("#merge"))
        await pg.click("#merge")  # confirm() wird automatisch bestätigt
        await pg.wait_for_function("state.items.length === 3 && !state.busy", timeout=240000)
        m = await pg.evaluate("state.items.map(i => ({ n: i.name, pg: i.pages, d: !!i.derived, sel: i.selected }))")
        P.check("Neue Gesamt-PDF", m[2]['d'] and m[2]['pg'] == 2 and m[2]['n'].endswith("_gesamt.pdf"), m)
        P.check("Originale abgewählt", not m[0]['sel'] and not m[1]['sel'], m)
        async with pg.expect_download() as dl:
            await pg.click("#apply")
        z2 = zipfile.ZipFile(io.BytesIO(open(await (await dl.value).path(), "rb").read()))
        names2 = z2.namelist()
        P.check("Nur Gesamt-PDF + Protokoll", len(names2) == 2, names2)
        pdf2 = [x for x in names2 if x.endswith(".pdf")][0]
        n2 = await pg.evaluate(PAGECOUNT, base64.b64encode(z2.read(pdf2)).decode())
        P.check("Gesamt-PDF hat 2 Seiten", n2 == 2, n2)
        log2 = z2.read([x for x in names2 if x.startswith("Protokoll")][0]).decode("utf-8-sig")
        P.check("Zusammenführen im Protokoll", "Zusammengeführt aus" in log2)

        # F) Verwerfen entfernt eine neu erstellte Datei
        await pg.evaluate("state.items[2].status = 'done'")  # nach dem Export wieder bearbeitbar machen
        await pg.evaluate("render()")
        await pg.click("button.discard")
        P.check("Verworfen", await pg.evaluate("state.items.length") == 2)

        P.check("Keine JS-Fehler", not errs, errs[:3])
        await b.close()
    P.ende()

asyncio.run(main())
