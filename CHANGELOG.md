# Änderungen

Alle nennenswerten Änderungen am Unterlagen-Sortierer werden hier festgehalten.

## 1.2.0 – 2026-11-06

Erste MVP-Version: neues Erscheinungsbild, automatische Dreh-Erkennung und
die Ergebnisse eines vollständigen Qualitätschecks.

### Verdrehte Scans werden erkannt und gerade gespeichert

- Seiten, die quer oder kopfüber eingescannt wurden, erkennt die
  Texterkennung jetzt von selbst: Sie liest die Seite in der richtigen
  Richtung, Dokumenttyp und Name stimmen wieder, und Miniatur, Vorschau
  und Teilen-Dialog zeigen die Seite gerade.
- „Seite drehen“ in der Vorschau und „drehen“ an jeder Seite im
  Teilen-Dialog drehen von Hand nach.
- Beim Speichern wird die Drehung in die Kopie (bzw. die geteilte oder
  zusammengeführte Datei) geschrieben – in der eAkte liegt ein gerades
  Dokument. Das Original bleibt wie immer unverändert; das Protokoll
  vermerkt „gerade gedreht gespeichert“.

### Behoben (aus dem Qualitätscheck)

- Die Bildvorschau (JPG/PNG) funktionierte im Ordnermodus nicht
  („Vorschau nicht möglich“).
- Die vergrößerte Seitenansicht im Teilen-Dialog lag HINTER dem Dialog
  und war kaum zu sehen; Esc schließt jetzt erst die Vergrößerung, dann
  den Dialog.
- Beim Teilen/Zusammenführen erzeugte Dateien wurden im Hintergrund
  unnötig komplett neu gelesen (doppelte Texterkennung).
- Nach dem Zusammenführen teilweise gelesener Stapel konnten Seitentexte
  im Teilen-Dialog zur falschen Seite angezeigt werden.
- Schnelles Öffnen/Schließen der Vorschau konnte Fehler im Hintergrund
  auslösen; außerdem kleinere Speicher-Aufräumarbeiten und
  Code-Vereinfachungen (gemeinsamer Seiten-Renderer, tote Reste entfernt).

### Neues, schlichtes Erscheinungsbild

Im Orgalytics-Stil (www.orgalytics.de als Anker) – an der Bedienung
ändert sich nichts:

- Weiße Flächen mit feinen Trennlinien statt grauer Kästen; klare, ruhige
  Typografie (Geist); abgerundete Ecken und Schatten stark reduziert.
- Aktionsknöpfe („Ordner wählen“, „Umbenennen“) jetzt in der Textfarbe –
  wie auf der Website; die Markenfarbe Blau bleibt sparsamer Akzent für
  Links, Markierungen und den Fortschrittsbalken.
- Neuer Startbildschirm mit kurzer Erklärung in der Bildsprache der Website.
- Dunkler Modus entsprechend überarbeitet.
- Alle Farben kommen weiterhin aus `programm/marke.js` – für andere
  Kunden-Designs genügt es, diese Datei zu tauschen.
### Entfernt

- „Personenliste laden“ (CSV). Die Funktion wurde in der Praxis nicht
  gebraucht; die Namenserkennung aus dem Dokument selbst bleibt
  unverändert.

## 1.1.0 – 2026-11-06

Vereinfachungen nach dem ersten Praxistest – es gibt keine Modi und keine
Einstellungen mehr, die der Service Point verstehen muss:

- **Eine Datei zum Starten:** Im obersten Ordner liegt nur noch
  `Unterlagen-Sortierer.html` (Doppelklick). Alles andere – Bibliotheken, Regeln,
  Anleitungen, Beispiel-Scans, Start-Helfer für Sonderfälle – liegt in `programm/`.
- **Ein fester Ablageweg:** Umbenannte Kopien kommen immer je Person in einen
  Unterordner von `umbenannt/`, die Originale wandern immer nach `verarbeitet/`.
  Die frühere Auswahl (Umbenennen-Modus, Personen-Haken) entfällt.
- **Namens-Vorgabe ist nur noch Lückenfüller:** Sie greift ausschließlich bei
  Dateien ohne erkannten Namen und überschreibt nie erkannte Namen – wichtig,
  wenn Unterlagen mehrerer Personen gemischt eingelesen werden.
- **Zusammenführen am richtigen Ort:** Zeilen ankreuzen → über der Liste erscheint
  „Zu einer PDF zusammenführen“. Unten rechts bleibt nur der Speichern-Knopf.
  Quellen bleiben sichtbar („Zusammengeführt in …“); bei gemischten Dokumenttypen
  wird das Ergebnis zur Prüfung gelb markiert.
- **Seiten-Lesen automatisch statt Einstellung:** Erst werden je Datei höchstens
  zwei Seiten per Texterkennung gelesen (die Liste steht schnell), danach liest
  das Programm die restlichen Seiten im Hintergrund nach – der Teilen-Dialog
  findet sie dann schon klassifiziert vor. Leere Seiten kosten nie Lesezeit.
- **Sortieren und teilen:** Im Dialog lassen sich die Seiten jetzt mit der Maus
  in eine neue Reihenfolge ziehen (der Trennvorschlag folgt der neuen Ordnung);
  nur Umsortieren oder Bereinigen ergibt „Sortiert speichern“. Seiten mehrerer
  Dateien: erst zusammenführen, dann sortieren.
- **Vorschau im selben Fenster:** Klick aufs Vorschaubild öffnet eine blätterbare
  Vorschau statt eines neuen Browser-Tabs; „In neuem Fenster öffnen“ bleibt als
  Extra. Neu: „Text kopieren“ legt den erkannten Text in die Zwischenablage
  (z. B. für einen DSGVO-konformen KI-Assistenten) – auch in jeder Tabellenzeile
  unter „Erkannten Text anzeigen“.

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
