# Unterlagen-Sortierer

Ein Offline-Werkzeug für Service Points in Verwaltungen (Sozialamt, Grundsicherung):
Es liest eingescannte Antragsunterlagen (PDF/JPG/PNG), erkennt **Dokumenttyp** und
**Person** und benennt die Dateien einheitlich um — z. B.
`Scan_0001.pdf → Mustermann_Erika_Antrag.pdf`. Die so benannten Dateien lassen sich
direkt per Drag & Drop in die eAkte ziehen, wo der Dateiname sofort sagt, was drin ist.

![Übersicht mit geprüften Vorschlägen](docs/uebersicht.png)

![Teilen-Dialog mit Seitenvorschau](docs/teilen-dialog.png)

## Funktionen

- **Erkennen & Umbenennen:** Dokumenttyp über editierbare Suchbegriffe (24 Typen ab Werk),
  Person über Personenliste, Formularfelder, Anschrift, Absender oder Briefanrede;
  Dateinamen-Muster frei kombinierbar; Ampel-Status je Datei, alles von Hand korrigierbar
- **Stapel-Scans teilen:** Seitenvorschau mit Zoom, automatisch vorgeschlagene Trennstellen,
  leere Rückseiten werden erkannt und weggelassen — Originale bleiben unverändert
- **Zusammenführen:** mehrere Dateien (auch Fotos) zu einer PDF verbinden
- **Mehrere Personen & laufender Betrieb:** Unterordner je Person, „Neue Dateien einlesen“
  für laufend eintreffende Scans, verarbeitete Originale wandern nach `verarbeitet/`
- **Nachvollziehbar:** nie überschreiben, Excel-taugliches Protokoll-CSV je Durchgang
- **100 % offline:** keine einzige Netzanfrage, automatisiert getestet —
  siehe [Datenschutz auf einen Blick](Unterlagen-Sortierer/Datenschutz.txt)

## Schnellstart

1. Das aktuelle Release-ZIP herunterladen und entpacken.
2. Starten per Doppelklick:
   - **Windows:** `Unterlagen-Sortierer starten.bat` (öffnet Microsoft Edge)
   - **macOS:** `Unterlagen-Sortierer starten.command` (beim ersten Start:
     Rechtsklick → „Öffnen“)
3. Ordner mit den Scans wählen (oder Dateien ins Fenster ziehen), Vorschläge prüfen,
   speichern. Fiktive Beispiel-Scans liegen im Ordner `Beispiel-Scans/`.

Keine Installation, keine Adminrechte, kein Internet nötig. Vollen Funktionsumfang
(Dateien direkt im Ordner umbenennen) bieten Edge und Chrome; andere Browser
speichern das Ergebnis als ZIP-Datei.

## Anpassen (ohne Programmierung)

| Datei | Zweck |
| --- | --- |
| `Unterlagen-Sortierer/regeln.js` | Dokumenttypen und Suchbegriffe, Standard-Dateinamenmuster |
| `Unterlagen-Sortierer/marke.js` | Name, Farben, Logo, Fußzeile (Corporate Design) |

Details: `Unterlagen-Sortierer/Hinweise fuer die IT.txt` und `LIESMICH.txt`.
Der Knopf **„Erkennungsregeln“** im Programm zeigt alle aktiven Begriffe an.

## Entwicklung

```bash
python3 -m pip install playwright pillow reportlab   # einmalig
python3 -m playwright install chromium                # einmalig
bash tests/alle_tests.sh                               # alle Tests (~150 Prüfungen)
bash tools/release_bauen.sh                            # Auslieferungs-ZIP bauen
```

Die gesamte Oberfläche und Logik steckt in `Unterlagen-Sortierer/app/index.html`
(eine Datei, kein Framework, kein Build-Schritt). Eingebettete Bibliotheken werden
mit `tools/bibliotheken_bauen.sh` aus festgepinnten npm-Paketen erzeugt.
Entwicklungs-Leitfaden: [CLAUDE.md](CLAUDE.md) · Änderungen: [CHANGELOG.md](CHANGELOG.md)

## Lizenz

[MIT](LICENSE) © 2026 Orgalytics · Kontakt: office@orgalytics.de

Eingebettete Bibliotheken und Schriften (pdf.js, Tesseract.js, pdf-lib, Geist, Lora)
stehen unter eigenen freien Lizenzen — siehe `Unterlagen-Sortierer/app/lib/lizenzen/`.
