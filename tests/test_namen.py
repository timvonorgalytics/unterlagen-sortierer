"""Namenserkennung (findName) direkt auf Textproben – schnell, ohne OCR.
Die Fälle stammen aus anonymisierten Kundenbeispielen (zwei Vornamen, Formular-Tabellen,
beschriftete Felder, Absenderblock, Briefanrede)."""
import asyncio, json
from playwright.async_api import async_playwright
from _gemeinsam import APP, Pruefer

P = Pruefer("Namenserkennung")

# (Beschreibung, Text, erwartet: nachname, vorname, quelle)
FAELLE = [
    ("Anschrift einfach", "Frau\nErika Mustermann\nLindenweg 4\n12345 Musterstadt", "Mustermann", "Erika", "Anschrift"),
    ("Anschrift zwei Vornamen", "Frau\nHelga Maria Brandt\nLindenweg 12\n12345 Musterstadt", "Brandt", "Helga Maria", "Anschrift"),
    ("Anschrift Ehepaar", "Herrn und Frau\nHans und Erika Mustermann\nLindenweg 4", "Mustermann", "Hans", "Anschrift"),
    ("Anschrift mit Straße dahinter", "Frau Erika Mustermann Lindenweg 4", "Mustermann", "Erika", "Anschrift"),
    ("Formular Name, Vorname", "1. Person\nName, Vorname: Mustermann, Erika\nGeburtsdatum: 12.08.1955", "Mustermann", "Erika", "Formularfeld"),
    ("Formular-Tabelle untereinander", "Familienname \nBrandt \nVorname(n) \nHelga   Maria \nGeburtsdatum \n14.03.1957", "Brandt", "Helga Maria", "Formularfeld"),
    ("Formular leeres Feld", "Familienname \nVorname \nGeburtsdatum \n14.03.1957", "", "", "nicht gefunden"),
    ("Feld Mieterin", "Mietbescheinigung\nMieterin   Helga Maria Brandt \nWohnung Lindenweg 12", "Brandt", "Helga Maria", "Formularfeld"),
    ("Feld Kontoinhaber", "Kontoauszug 10/2026\nKontoinhaber   Helga Maria Brandt \nIBAN DE09", "Brandt", "Helga Maria", "Formularfeld"),
    ("Feld Patientin", "Ärztliche Bescheinigung\nPatientin: Helga Maria Brandt, geb. 14.03.1957", "Brandt", "Helga Maria", "Formularfeld"),
    ("Vermieter zählt nicht als Mieter", "Der Vermieter Gerhard Kowalski bestätigt den Einzug.\nSehr geehrte Frau Brandt, hiermit", "Brandt", "", "Anrede"),
    ("Absenderblock", "Helga Maria Brandt\nLindenweg 12\n12345 Musterstadt\n\nStadt Musterstadt\nFachbereich Soziales", "Brandt", "Helga Maria", "Absender"),
    ("Absender nicht bei Firma", "Sparkasse Musterstadt\nMarktplatz 5\n12345 Musterstadt\nKontostand 876,98", "", "", "nicht gefunden"),
    ("Briefanrede", "Stadtwerke Musterstadt\nAbschlagsplan Strom\nSehr geehrte Frau Brandt,\nIhre Abschläge wurden neu festgesetzt.", "Brandt", "", "Anrede"),
    ("Vermieter-Zeile übersprungen", "zwischen\nHerrn Klaus Becker, Gartenstraße 9\n- Vermieter -\nund\nFrau Erika Mustermann\n- Mieter -", "Mustermann", "Erika", "Anschrift"),
    ("Nichts gefunden", "Unleserlich\n...\nxx", "", "", "nicht gefunden"),
]

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page()
        errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto(APP)
        for desc, text, nn, vn, src in FAELLE:
            r = await pg.evaluate("(t) => findName(t)", text)
            ok = r["nachname"] == nn and r["vorname"] == vn and r["src"] == src
            P.check(desc, ok, f"→ {json.dumps(r, ensure_ascii=False)}")
        P.check("Keine JS-Fehler", not errs, errs[:3])
        await b.close()
    P.ende()

asyncio.run(main())
