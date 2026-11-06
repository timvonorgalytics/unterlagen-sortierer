"""Dokumenttyp-Regeln (classify) direkt auf Textproben – schnell, ohne OCR.
Deckt die neuen Praxis-Typen ab und schützt die bestehenden vor Regressionen.
Außerdem: Dateien-Ablegen per Drag & Drop und der Filter „Nur zu prüfende anzeigen“."""
import asyncio, json
from playwright.async_api import async_playwright
from _gemeinsam import APP, Pruefer

P = Pruefer("Regeln")

# (Beschreibung, Text, erwarteter Typ, muss sicher sein)
FAELLE = [
    ("Ärztliche Bescheinigung", "Ärztliche Bescheinigung\nzur Vorlage beim Träger der Sozialhilfe - Mehrbedarf für Ernährung\n"
     "Patientin: Helga Maria Brandt\nDiagnose: Zöliakie (ICD-10: K90.0)\nDauer der Krankenkost: unbefristet", "Arztbescheinigung", True),
    ("Kündigung", "Kündigung meines Telefonvertrags\nSehr geehrte Damen und Herren,\nhiermit kündige ich meinen Vertrag "
     "fristgerecht zum nächstmöglichen Zeitpunkt.\nBitte bestätigen Sie das Vertragsende schriftlich.", "Kuendigung", True),
    ("Mahnung", "Zahlungserinnerung\nSehr geehrte Frau Brandt,\nfür die Rechnung vom 01.10.2026 ist noch ein offener Betrag "
     "von 48,00 EUR verzeichnet.\nBitte zahlen Sie innerhalb der Zahlungsfrist, sonst fällt eine Mahngebühr an.", "Mahnung", True),
    ("Antrag bleibt Antrag", "Antrag auf Leistungen der Grundsicherung im Alter und bei Erwerbsminderung\n"
     "Hiermit beantrage ich Leistungen nach dem SGB XII.\nUnterschrift des Antragstellers", "Antrag", True),
    ("Kontoauszug bleibt Kontoauszug", "Kontoauszug 10/2026\nAlter Kontostand 876,98\nBuchungstag Wertstellung\n"
     "Neuer Kontostand 598,32\nIBAN DE09", "Kontoauszug", True),
    ("Mietvertrag trotz Kündigungsfrist", "Wohnraummietvertrag\nzwischen Vermieter und Mieter\n§ 1 Mietsache\n"
     "Nettokaltmiete 420,00 EUR, Kaution 840 EUR\nMietbeginn 01.04.2019\nDie Kündigungsfrist beträgt drei Monate.", "Mietvertrag", True),
]

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page()
        errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto(APP)
        for desc, text, typ, sure in FAELLE:
            r = await pg.evaluate("(t) => classify(t)", text)
            ok = r["type"] == typ and (r["sure"] == sure)
            P.check(desc, ok, f"→ {json.dumps(r, ensure_ascii=False)[:120]}")
        # Drag & Drop: eine Datei aufs Fenster ziehen landet in der Liste
        n = await pg.evaluate("""async () => {
            const dt = new DataTransfer();
            dt.items.add(new File([new Uint8Array([37, 80, 68, 70])], "abgelegt.pdf", { type: "application/pdf" }));
            window.dispatchEvent(new DragEvent("drop", { dataTransfer: dt, cancelable: true }));
            await new Promise((r) => setTimeout(r, 200));
            return state.items.length;
        }""")
        P.check("Drag & Drop nimmt Dateien an", n == 1, n)
        await pg.wait_for_function("!state.busy", timeout=60000)
        # Filter: Checkbox vorhanden und blendet sichere Zeilen aus
        await pg.evaluate("""() => {
            state.items[0].status = "done"; state.items[0].manual = { type: true, nachname: true };
            state.items[0].type = "Antrag"; state.items[0].nachname = "Mustermann"; render();
        }""")
        P.check("Zeile sichtbar ohne Filter", await pg.evaluate("!state.items[0].tr.classList.contains('hidden')"))
        await pg.check("#onlycheck")
        await pg.evaluate("state.items.forEach(applyRowFilter)")
        P.check("Filter blendet sichere Zeile aus", await pg.evaluate("state.items[0].tr.classList.contains('hidden')"))
        # Regeln-Dialog (nur Ansicht): öffnet, zeigt alle Typen mit Begriffen, schließt
        await pg.click("#rules")
        P.check("Regeln-Dialog offen", await pg.evaluate("document.querySelector('#rulesdlg').open"))
        txt = await pg.inner_text("#rulesbody")
        P.check("Alle Typen gelistet", all(t in txt for t in ["Kontoauszug", "Mietbescheinigung", "Mahnung", "Arztbescheinigung"]), txt[:120])
        P.check("Begriffe sichtbar", "Alter Kontostand" in txt and "Zahlungserinnerung" in txt)
        n_stark = await pg.evaluate("document.querySelectorAll('#rulesbody .kw.stark').length")
        n_schwach = await pg.evaluate("document.querySelectorAll('#rulesbody .kw.schwach').length")
        P.check("Starke und schwache Chips", n_stark > 50 and n_schwach > 50, (n_stark, n_schwach))
        await pg.click("#rulesclose")
        P.check("Regeln-Dialog geschlossen", await pg.evaluate("!document.querySelector('#rulesdlg').open"))
        P.check("Keine JS-Fehler", not errs, errs[:3])
        await b.close()
    P.ende()

asyncio.run(main())
