"""Erzeugt die fiktiven Testunterlagen in tests/testdocs (Scans als Bild-PDF, Handyfoto, digitales PDF).
Aufruf: python3 tests/testdocs_erzeugen.py   (braucht pillow + reportlab)
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "testdocs"))
random.seed(4)
# Schriften: Linux (DejaVu) oder macOS (Arial)
def _font(*cands):
    for c in cands:
        if os.path.exists(c): return c
    raise SystemExit("Keine passende Schrift gefunden: " + ", ".join(cands))
F = _font("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/System/Library/Fonts/Supplemental/Arial.ttf", "/Library/Fonts/Arial.ttf")
FB = _font("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/Library/Fonts/Arial Bold.ttf")
def _blatt(lines, rot, noise):
    W, H = 1654, 2339  # A4 @200 dpi
    im = Image.new("L", (W, H), 250); d = ImageDraw.Draw(im); y = 150
    for l in lines:
        bold = l.startswith("#"); t = l.lstrip("#")
        size = 46 if bold else 30
        d.text((150, y), t, fill=20, font=ImageFont.truetype(FB if bold else F, size)); y += size + (22 if bold else 16)
    im = im.rotate(rot, fillcolor=250, resample=Image.BICUBIC)
    if noise:
        px = im.load()
        for _ in range(9000): px[random.randrange(W), random.randrange(H)] = random.choice([60, 120, 200])
        im = im.filter(ImageFilter.GaussianBlur(0.5))
    return im

def scan(name, lines, rot=0.6, ext="pdf", noise=True):
    W, H = 1654, 2339
    im = _blatt(lines, rot, noise)
    if ext == "pdf": im.convert("RGB").save(name, "PDF", resolution=200)
    else: im.convert("RGB").resize((W*3//4, H*3//4)).save(name, "JPEG", quality=70)

def scan_mehrseitig(name, seiten, rot=0.5, noise=True):
    """Stapel-Scan: mehrere Blätter in einer PDF (für die Funktion „Teilen“)."""
    imgs = [_blatt(lines, rot, noise).convert("RGB") for lines in seiten]
    imgs[0].save(name, "PDF", resolution=200, save_all=True, append_images=imgs[1:])

scan("Scan_0001.pdf", ["#Antrag auf Leistungen der Grundsicherung", "#im Alter und bei Erwerbsminderung (SGB XII)", "",
  "1. Angaben zur antragstellenden Person", "Name, Vorname: Mustermann, Erika", "Geburtsdatum: 12.08.1955",
  "Anschrift: Lindenweg 4, 12345 Musterstadt", "Familienstand: verheiratet", "",
  "2. Angaben zum Ehegatten", "Name, Vorname: Mustermann, Hans", "", "Hiermit beantrage ich Leistungen nach dem SGB XII.",
  "Musterstadt, den 03.11.2026", "Unterschrift des Antragstellers"])
scan("Scan_0002.pdf", ["#Sparkasse Musterstadt", "Frau", "Erika Mustermann", "Lindenweg 4", "12345 Musterstadt", "",
  "#Kontoauszug 10/2026", "IBAN DE12 3456 7890 1234 5678 90", "Alter Kontostand vom 30.09.2026     412,17 EUR",
  "Buchungstag  Wertstellung  Vorgang                    Betrag", "01.10.  01.10.  Lastschrift Miete            -520,00",
  "15.10.  15.10.  Gutschrift Rente               +840,55", "Neuer Kontostand vom 31.10.2026     598,32 EUR"], rot=-0.8)
scan("Scan_0003.pdf", ["#Wohnraummietvertrag", "", "zwischen", "Herrn Klaus Becker, Gartenstraße 9, 12345 Musterstadt", "- Vermieter -",
  "und", "Frau Erika Mustermann und Herrn Hans Mustermann", "- Mieter -", "", "§ 1 Mietsache", "Vermietet wird die Wohnung Lindenweg 4, 2. OG,",
  "Wohnfläche 58 m². Mietbeginn: 01.04.2019", "§ 2 Miete", "Nettokaltmiete 420,00 EUR, Vorauszahlung Betriebskosten 100,00 EUR"], rot=0.4)
scan("Scan_0004.pdf", ["#Deutsche Rentenversicherung Bund", "", "Herrn", "Hans Mustermann", "Lindenweg 4", "12345 Musterstadt", "",
  "Ihr Ansprechpartner: Frau Petra Weber, Telefon 030 1234-56", "Versicherungsnummer 12 120855 M 003", "",
  "#Rentenbescheid", "Bescheid über Ihre Rente wegen Alters", "Altersrente für langjährig Versicherte ab 01.09.2021",
  "Der monatliche Zahlbetrag beträgt ab 01.12.2026: 1.012,40 EUR"], rot=1.0)
scan("Scan_0005.pdf", ["#AOK Musterland - Die Gesundheitskasse", "", "Frau", "Erika Mustermann", "Lindenweg 4, 12345 Musterstadt", "",
  "#Mitgliedsbescheinigung", "Hiermit bestätigen wir, dass Frau Erika Mustermann, geb. 12.08.1955,",
  "seit dem 01.01.2020 bei uns als Rentnerin krankenversichert ist.", "Musterstadt, 28.10.2026"], rot=-0.5)
scan("Scan_0006.pdf", ["#Hausverwaltung Becker", "Herrn und Frau", "Hans und Erika Mustermann", "", "#Betriebskostenabrechnung 2025",
  "Abrechnungszeitraum 01.01.2025 bis 31.12.2025", "Ihre Vorauszahlungen: 1.200,00 EUR", "Ihr Anteil: 1.343,20 EUR",
  "Nachzahlung: 143,20 EUR", "Umlageschlüssel: Wohnfläche"], rot=0.7)
scan("Foto_Ausweis.jpg", ["#BUNDESREPUBLIK DEUTSCHLAND", "#PERSONALAUSWEIS / IDENTITY CARD", "", "Name: MUSTERMANN", "Vornamen: ERIKA",
  "Geburtstag: 12.08.1955", "Staatsangehörigkeit: DEUTSCH", "Gültig bis: 01.06.2031"], rot=2.0, ext="jpg")
scan("Scan_0008.pdf", ["Unleserlich", "...", "xx"], rot=0)  # leeres/schlechtes Blatt

# digitales PDF (mit Textebene)
c = canvas.Canvas("Rentenanpassung_digital.pdf", pagesize=A4)
c.setFont("Helvetica-Bold", 14); c.drawString(70, 780, "Deutsche Rentenversicherung")
c.setFont("Helvetica", 11)
for i, l in enumerate(["Herrn", "Hans Mustermann", "Lindenweg 4", "12345 Musterstadt", "", "Rentenanpassung zum 01.07.2026",
  "Mitteilung über die Anpassung Ihrer Rente", "Ihre Rente erhöht sich ab 01.07.2026 auf 1.012,40 EUR."]):
    c.drawString(70, 740 - i*16, l)
c.save()

# Stapel-Scan: Antrag (2 Seiten), eine LEERE Rückseite, Kontoauszug (2 Seiten) in EINER Datei
# → zum Testen der Funktionen „Teilen“ und „leere Seiten weglassen“
scan_mehrseitig("Scan_0007_Stapel.pdf", [
  ["#Antrag auf Leistungen der Grundsicherung", "#im Alter und bei Erwerbsminderung (SGB XII)", "",
   "1. Angaben zur antragstellenden Person", "Name, Vorname: Mustermann, Erika", "Geburtsdatum: 12.08.1955",
   "Anschrift: Lindenweg 4, 12345 Musterstadt", "", "Hiermit beantrage ich Leistungen nach dem SGB XII."],
  ["#Abschnitt 3 - Einkommen", "", "Renteneinkommen: 840,55 EUR monatlich", "Sonstiges Einkommen: keines", "",
   "Ich versichere die Richtigkeit der Angaben.", "Musterstadt, den 05.11.2026", "Unterschrift der Antragstellerin"],
  [],   # leere Rückseite (Duplex-Scan)
  ["#Sparkasse Musterstadt", "Frau", "Erika Mustermann", "Lindenweg 4", "12345 Musterstadt", "",
   "#Kontoauszug 09/2026", "IBAN DE12 3456 7890 1234 5678 90", "Alter Kontostand vom 31.08.2026     389,70 EUR",
   "Buchungstag  Wertstellung  Vorgang                    Betrag", "01.09.  01.09.  Lastschrift Miete            -520,00",
   "15.09.  15.09.  Gutschrift Rente               +840,55", "Neuer Kontostand vom 30.09.2026     412,17 EUR"],
  ["#Sparkasse Musterstadt - Seite 2", "Fortsetzung Kontoauszug 09/2026", "",
   "Buchungstag  Wertstellung  Vorgang                    Betrag", "18.09.  18.09.  Lastschrift Strom             -62,00",
   "22.09.  22.09.  Ueberweisung Apotheke             -18,40"]], rot=0.4)
