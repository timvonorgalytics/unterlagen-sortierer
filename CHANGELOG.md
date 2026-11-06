# Änderungen

Alle nennenswerten Änderungen am Unterlagen-Sortierer werden hier festgehalten.

## 1.0.0 – 2026-11-06

Erste veröffentlichte Version.

### Erkennen und Umbenennen
- Liest PDF-, JPG- und PNG-Dateien aus einem Ordner (oder per Dateiauswahl / Drag & Drop)
- Texterkennung vollständig lokal: PDF-Textebene, sonst OCR (Tesseract, Deutsch)
- Erkennt den Dokumenttyp anhand editierbarer Regeln (`regeln.js`, 24 Typen ab Werk)
  und die Person (Personenliste-CSV, Vorgabe, Formularfelder – auch mit zwei Vornamen
  und Wert in der Folgezeile –, Anschrift, Absenderblock, Briefanrede)
- Dateinamen-Muster frei kombinierbar: `{Nachname}_{Vorname}_{Dokumenttyp}_{Datum}_{Original}`
- Ampel-Status je Datei (Sicher / Bitte prüfen / Name fehlt), alles von Hand korrigierbar
- Knopf „Erkennungsregeln“: zeigt alle Typen und Suchbegriffe im Programm an

### Teilen und Zusammenführen
- Stapel-Scans mit mehreren Dokumenten in einer PDF werden erkannt („Teilen …“):
  Seitenvorschau mit Zoom, automatisch vorgeschlagene Trennstellen, per Klick korrigierbar
- Leere Rückseiten (Duplex-Scan) werden erkannt und weggelassen; jede Seite einzeln
  behaltbar/weglassbar
- Markierte Dateien lassen sich zu einer PDF zusammenführen (Fotos werden als Seiten eingebettet)
- Originale bleiben dabei stets unverändert

### Arbeiten mit mehreren Personen und im laufenden Betrieb
- Ohne Vorgabe wird der Name je Dokument erkannt – mehrere Personen pro Durchlauf
- Haken „Je Person einen Unterordner anlegen“ (auch als Pfade in der ZIP)
- „Neue Dateien einlesen“ holt nur neue Dateien; erledigte Zeilen verschwinden
- Kopien-Modus verschiebt verarbeitete Originale in den Unterordner `verarbeitet` –
  der Scan-Ordner zeigt immer nur die offene Arbeit, auch nach einem Neustart
- Stammordner-Prinzip: Danach zugezogene Dateien/Ordner (z. B. Mail-Anhänge) ergänzen
  die Liste und werden in den Stammordner gespeichert; fremde Originale bleiben unberührt

### Speichern und Nachvollziehbarkeit
- Kopien im Unterordner „umbenannt“, Originale umbenennen oder (ohne Ordnerzugriff)
  ZIP-Download; nie wird etwas überschrieben (`_2`, `_3`, …)
- Jeder Durchgang schreibt ein Excel-taugliches Protokoll-CSV mit Herkunfts-Hinweisen

### Plattform und Datenschutz
- Läuft ohne Installation und ohne Adminrechte per Doppelklick: Windows (`.bat`, Edge)
  und macOS (`.command`, Chrome/Edge)
- 100 % offline, keine einzige Netzanfrage (automatisiert getestet); Näheres in
  `Unterlagen-Sortierer/Datenschutz.txt`
- Branding (`marke.js`) und Regeln (`regeln.js`) ohne Programmierung austauschbar
