"""Erkennung (Typ + Name) in drei Situationen und ZIP-Export – Programm direkt von der Festplatte (file://) geöffnet."""
import asyncio, io, zipfile
from playwright.async_api import async_playwright
from _gemeinsam import APP, DOCS, DOCS_DIR, Pruefer

TYP = {"Foto_Ausweis.jpg": "Ausweis", "Rentenanpassung_digital.pdf": "Rentenanpassung", "Scan_0001.pdf": "Antrag",
       "Scan_0002.pdf": "Kontoauszug", "Scan_0003.pdf": "Mietvertrag", "Scan_0004.pdf": "Rentenbescheid",
       "Scan_0005.pdf": "Krankenversicherung", "Scan_0006.pdf": "Nebenkostenabrechnung",
       "Scan_0007_Stapel.pdf": "Antrag", "Scan_0008.pdf": "Sonstiges"}
PERS = {"Foto_Ausweis.jpg": "Mustermann Erika", "Rentenanpassung_digital.pdf": "Mustermann Hans", "Scan_0001.pdf": "Mustermann Erika",
        "Scan_0002.pdf": "Mustermann Erika", "Scan_0003.pdf": "Mustermann Erika", "Scan_0004.pdf": "Mustermann Hans",
        "Scan_0005.pdf": "Mustermann Erika", "Scan_0006.pdf": "Mustermann Hans",
        "Scan_0007_Stapel.pdf": "Mustermann Erika", "Scan_0008.pdf": " "}
P = Pruefer("Dateimodus")

async def run(pg, setup_js=None, plist=None):
    await pg.goto(APP)
    if plist: await pg.set_input_files("#plistfile", plist); await pg.wait_for_timeout(200)
    if setup_js: await pg.evaluate(setup_js)
    await pg.set_input_files("#filepick", DOCS)
    await pg.wait_for_function("state.items.length && !state.busy", timeout=240000)
    return await pg.evaluate("state.items.map(i=>({d:i.originalName||i.name,t:i.type,n:(i.nachname+' '+i.vorname),src:i.nameSrc,st:rowState(i)[0],neu:buildName(i)}))")

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(accept_downloads=True, viewport={"width": 1440, "height": 1100})
        errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        # A) ohne Vorgabe
        for r in await run(pg):
            P.check(f"Typ {r['d']}", r['t'] == TYP[r['d']], f"→ {r['t']}")
            P.check(f"Name {r['d']}", r['n'] == PERS[r['d']], f"→ '{r['n']}' ({r['src']})")
        # B) Vorgabe ist nur Lückenfüller: greift bei Scan_0008 (kein Name), überschreibt sonst nichts
        rows = await run(pg, "document.querySelector('#vNach').value='Mustermann';document.querySelector('#vVor').value='Erika'")
        r8 = next(r for r in rows if r['d'] == "Scan_0008.pdf")
        P.check("Vorgabe füllt Unbekannte", r8['n'] == "Mustermann Erika" and r8['src'] == "Vorgabe", r8)
        for r in rows:
            if r['d'] == "Scan_0008.pdf": continue
            P.check(f"Vorgabe überschreibt nicht {r['d']}", r['n'] == PERS[r['d']] and r['src'] != "Vorgabe", f"{r['n']} ({r['src']})")
        P.check("Dateiname Antrag", any(r['neu'] == "Mustermann_Erika_Antrag.pdf" for r in rows))
        # C) Personenliste
        rows = await run(pg, plist=str(DOCS_DIR / "personen.csv"))
        info = await pg.inner_text("#plistinfo"); P.check("Personenliste geladen", "3 Personen" in info, info)
        for r in rows:
            if r['d'] == "Scan_0008.pdf": continue
            P.check(f"Liste {r['d']}", r['src'] == "Personenliste" and r['n'] in ("Mustermann Erika", "Mustermann Hans"), f"{r['n']} {r['src']}")
        P.check("Rentenbescheid → Hans", next(r for r in rows if r['d'] == "Scan_0004.pdf")['n'] == "Mustermann Hans")
        # D) manuelle Korrektur + ZIP
        await pg.fill("tbody tr:nth-child(10) input.name >> nth=0", "Mustermann")
        await pg.fill("tbody tr:nth-child(10) input.name >> nth=1", "Erika")
        await pg.select_option("tbody tr:nth-child(10) select", "Kontoauszug")
        P.check("Manuell korrigiert = sicher", await pg.evaluate("rowState(state.items[9])[0]") == "ok")
        await pg.click("tbody tr:nth-child(1) input[type=checkbox]")
        async with pg.expect_download() as dl:
            await pg.click("#apply")
        z = zipfile.ZipFile(io.BytesIO(open(await (await dl.value).path(), "rb").read()))
        names = z.namelist()
        P.check("ZIP gültig", z.testzip() is None)
        P.check("9 Dateien + Protokoll", len(names) == 10, names)
        P.check("Abgewählte Datei fehlt", not any("Ausweis" in n for n in names))
        P.check("Pfade je Person", "Mustermann_Erika/Mustermann_Erika_Kontoauszug.pdf" in names
                and any(n.startswith("Mustermann_Hans/") for n in names), names)
        P.check("Doppelte Namen nummeriert", "Mustermann_Erika/Mustermann_Erika_Kontoauszug_2.pdf" in names, names)
        P.check("Inhalt unverändert", z.read("Mustermann_Erika/Mustermann_Erika_Antrag.pdf") == (DOCS_DIR / "Scan_0001.pdf").read_bytes())
        log = z.read([n for n in names if n.startswith("Protokoll")][0]).decode("utf-8-sig")
        P.check("Protokoll lesbar", "Originalname" in log and "Scan_0001.pdf" in log)
        P.check("Keine JS-Fehler", not errs, errs[:3])
        await b.close()
    P.ende()
asyncio.run(main())
