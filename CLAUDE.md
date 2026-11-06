# Unterlagen-Sortierer

Offline-Programm für Verwaltungen (Sozialamt, Grundsicherung): liest eingescannte Unterlagen (PDF/JPG/PNG)
aus einem Ordner, erkennt Dokumenttyp und Person und benennt die Dateien nach Muster um
(`Mustermann_Erika_Kontoauszug.pdf`). Betreiber: Orgalytics. Kunden: Windows-PCs mit Edge, oft ohne
Adminrechte. Ausgeliefert als ZIP; Start per Doppelklick auf `Unterlagen-Sortierer.html` – die EINZIGE
Datei auf oberster Ebene des Produkts (Leitsatz von Tim: Mitarbeitende dürfen nie raten müssen, was sie
anklicken; es gibt keine Modi und keine Einstellungen, die der Service Point verstehen muss).

## Unverhandelbare Regeln

1. **Komplett offline.** Keine CDN-Links, kein fetch() ins Netz, keine Telemetrie. `tests/test_offline.py`
   prüft, dass keine einzige Netzanfrage entsteht. Das ist das zentrale Datenschutzversprechen.
2. **Keine echten Bürgerdaten** in diesem Projekt oder in Prompts. Nur fiktive/anonymisierte Testunterlagen
   (`tests/testdocs`, Personen „Mustermann“). Echte Problemfälle vom Kunden nur anonymisiert nachbauen.
3. **Vor jeder Übergabe `tests/alle_tests.sh`** – alle Tests müssen bestehen. Neue Funktion = neuer Test.
4. **CI nur über `programm/marke.js`.** Keine Markenwerte (Farben, Namen, Logo) in der HTML hart
   kodieren. Quelle der Orgalytics-Werte: die internen Markenvorlagen. Nie Farben oder Texte raten.
   Designsprache (seit 1.2.0, Anker: www.orgalytics.de): weiße Flächen, Haarlinien (`--line`),
   Radius 2–6 px, keine Karten-Schatten; Aktionsknöpfe (`.btn.primary`) in Textfarbe (`--action`,
   im Dunkelmodus invertiert), Markenblau NUR als Akzent (Links, Auswahl, Fortschritt, Fokus und
   das Lora-kursive Akzentwort im Startbildschirm). Überschriften in Geist, Lora nur kursiv als Akzent.
5. **Kein Build-Schritt für Kunden.** Das Programm muss als entpackter Ordner per file:// laufen.
   Auf oberster Ebene liegt genau EINE Datei (`Unterlagen-Sortierer.html`); release_bauen.sh erzwingt das.
6. Oberfläche und Texte auf Deutsch, Satzanfang groß, aktive Verben („Dateien umbenennen“, nicht „Absenden“).

## Aufbau

```
Unterlagen-Sortierer/                ← das Auslieferungsprodukt (wird gezippt)
  Unterlagen-Sortierer.html          die EINZIGE Datei oben: Doppelklick = Start im Standardbrowser;
                                     gesamte Oberfläche + Logik (ein File, kein Framework)
  programm/
    Start mit Edge.bat               Windows-Helfer, falls der Standardbrowser nicht Edge/Chrome ist (nur ASCII, CRLF!)
    Start mit Chrome oder Edge.command  macOS-Helfer (LF, ausführbar!)
    regeln.js      Dokumenttypen + Suchbegriffe (vom Kunden-IT editierbar)  → window.REGELN
    marke.js       Name, Farben, Logo-SVG, Fußzeile                        → window.MARKE
    version.js     wird von release_bauen.sh aus VERSION erzeugt           → window.APP_VERSION
    LIESMICH.txt, Hinweise fuer die IT.txt, Datenschutz.txt, Lizenz.txt
    Beispiel-Scans/  (wird von tools/release_bauen.sh aus tests/testdocs befüllt)
    lib/           gebaute Bibliotheken – NICHT von Hand ändern, nur via tools/bibliotheken_bauen.sh
tests/             Playwright-Tests (Python) + fiktive Testunterlagen
tools/             bibliotheken_bauen.sh, release_bauen.sh
VERSION            Versionsnummer für das Release-ZIP
```

### Ablauf in Unterlagen-Sortierer.html

`pickFolder()`/`pickFiles()` → `start()` (parallel, Anzahl = halbe Kerne, max. 3) → `readText()`
(PDF: Textebene per pdf.js, sonst Seite rendern → Tesseract; Bilder → Tesseract) → `analyse()`
= `classify()` + `findName()` + `findDate()` → Tabelle → `backgroundScan()` → `apply()` →
`applyFolder()` (Ordnerzugriff) oder `applyZip()` (Ersatz ohne Ordnerzugriff, eigener ZIP-Schreiber).

- **Seiten-Lesen (automatische Regel, KEINE Einstellung):** `readText()` liest im ersten Durchgang
  höchstens 2 Seiten per OCR (Textseiten digitaler PDFs kosten fast nichts → alle, Kappe 40; leere
  Seiten per `inkRatio < 0.004` erkannt, kosten kein Budget, Text ""). `item.pagesRead` zählt mit –
  auch beim Teilen/Zusammenführen erzeugte Dateien setzen es, sonst liest `backgroundScan()` sie
  unnötig noch einmal. Seiten rendert überall `renderPage(page, scale, rot)` (Maßstäbe: `ocrScale`
  ≈2600 px, `fitScale` für Anzeige) – kein Copy-&-Paste von Canvas-Code.
- **Dreh-Erkennung (`ocrSmart`):** Jede OCR läuft über `ocrSmart(canvas)`. Güte = Tesseract-Konfidenz
  × Anteil echter Wörter (`Konfidenz × min(1, Wörter/8)`; Tesseract gibt seitwärts gelesenem Müll
  sonst noch ~45). Unter 50 wird die Seite um 90/270/180 gedreht erneut gelesen und die beste
  Richtung übernommen. Ergebnis in `item.pageRot[]` (Grad im Uhrzeigersinn, die die Seite gerade
  stellen); `item.thumb`/`rec.thumb` sind bereits gedreht (`thumbRot` merkt sich, wie weit –
  `setRotDisplay()` dreht nach). Von Hand: „Seite drehen“ in der Vorschau, „drehen“ je Seite im
  Teilen-Dialog. Beim Speichern schreibt `outputData(it)` die Drehung in die KOPIE (pdf-lib
  `setRotation` bzw. Foto-Pixel neu kodiert; Fehlschlag → unveränderte Kopie); `doSplit`/
  `mergeSelected` drehen über `turnPage()` direkt beim Erzeugen, die neuen Dateien gelten als
  gerade (`pageRot` = 0). Das Original bleibt IMMER unangetastet.
  Danach liest `backgroundScan()` die restlichen Seiten mehrseitiger PDFs leise nach (pausiert bei
  `state.busy` und offenem Teilen-Dialog, bricht ab, wenn die Zeile verschwindet): Es füllt NUR
  `pageTexts`/`multiHint` – Typ/Name angezeigter Zeilen werden NIE nachträglich geändert, und eine
  Zeile, in der gerade getippt wird, wird nicht neu gezeichnet. Der Teilen-Dialog nutzt die so
  gelesenen Seiten als Cache (sofort klassifiziert) und liest nur den Rest selbst.

- **classify:** Begriffe aus regeln.js, normalisiert (`norm()`: klein, ä→ae, ß→ss, nur a-z0-9).
  `stark` = 3 Punkte, `schwach` = 1; im Kopf der Seite (erste 450 Zeichen) ×1,5.
  „Sicher“ wenn ≥ 3 Punkte und ≥ 1,5× der Zweitplatzierte.
- **findName (Reihenfolge):** Formularfelder
  („Name, Vorname:“; „Familienname/Nachname“ und „Vorname(n)“ auch mit Wert in der NÄCHSTEN Zeile
  (Formular-Tabellen) und mit zwei Vornamen; beschriftete Voll-Namen-Felder Mieter(in)/Patient(in)/
  Kontoinhaber(in)/Versicherungsnehmer(in)) → Anschrift („Herrn/Frau“, auch allein in einer Zeile mit
  Leerzeilen danach, „Herrn und Frau Hans und Erika …“, zwei Vornamen „Frau Helga Maria Brandt“ →
  letztes Wort = Nachname, außer es ist eine Straße) → Absenderblock (Namenszeile direkt über
  „Straße + Hausnummer“, keine Firmen/Behörden via `ORGA`) → Briefanrede („Sehr geehrte Frau X“, nur
  Nachname). Zeilen mit Ansprechpartner, Sachbearbeiter, Vermieter usw. (`NOT_PERSON`) und Namen direkt
  über „- Vermieter -“ werden übersprungen; `FELDWORT` verhindert, dass Beschriftungen („Vorname“,
  „Geburtsdatum“) als Namen durchgehen. Quellen-Vertrauen: Formularfeld sicher, Anschrift/Absender/
  Anrede unsicher („Bitte prüfen“). Die Vorgabe aus den Eingabefeldern ist NUR Lückenfüller: Sie greift
  erst, wenn das Dokument keinen Namen hergibt – erkannte Namen werden nie überschrieben (Tims Regel
  für Stapel mit mehreren Personen). Fälle in `tests/test_namen.py` (direkt auf findName, ohne OCR).
- **Manuelle Änderungen** stehen in `item.manual` und werden beim Neu-Auswerten nicht überschrieben.
- **Sortieren und teilen (Stapel-Scans):** Jede mehrseitige PDF hat „Sortieren und teilen …“ →
  `openSplit()` zeigt erst ALLE Miniaturen, dann wird jede Seite klassifiziert (Cache aus
  `backgroundScan()`, sonst Textebene/OCR) und Trennstellen vorgeschlagen (`proposeCuts` auf der
  ANGEZEIGTEN Reihenfolge: neuer Abschnitt, sobald eine Seite *sicher* einen anderen Typ hat).
  Seiten sind per Drag & Drop umsortierbar (`split.order`, `movePage()` → Vorschlag wird neu
  berechnet); Trennstellen per Klick änderbar; leere Seiten (inkRatio) sind vorab „weglassen“.
  `doSplit()` erzeugt per **pdf-lib** je Abschnitt eine neue PDF in Anzeige-Reihenfolge
  (`copyPages` mit beliebiger Index-Folge); 1 Abschnitt + umsortiert/bereinigt → „Sortiert
  speichern“/eine Datei (`_sortiert`/`_bereinigt`). Original bleibt unverändert, wird abgewählt.
  `analyse()`/`backgroundScan()` setzen `item.multiHint` → gelber Hinweis in der Typ-Spalte
  (Seiten-Klassifikationen cached `surePageTypes()`, denn `reanalyseAll()` feuert je Tastendruck).
  Die Zoom-Ansicht `#zoom` liegt IM `<dialog>` – ein Element außerhalb kann den modalen Top-Layer
  nie überdecken (so war der Zoom unsichtbar); Esc schließt erst den Zoom, dann den Dialog
  (`cancel`-Handler mit `preventDefault`).
- **Vorschau + Text kopieren:** Klick aufs Thumbnail → Overlay `#preview` im selben Fenster
  (`openPreview`, blätterbar, Esc/Klick daneben schließt; „In neuem Fenster öffnen“ als Extra).
  `copyText()` (Clipboard-API mit execCommand-Fallback) liegt in der Vorschau und an „Erkannten
  Text anzeigen“ – Zweck: erkannten Text in den DSGVO-konformen KI-Assistenten der Kunden kopieren.
- **Zusammenführen:** Leiste ÜBER der Tabelle, sobald ≥ 2 Zeilen markiert sind („Zu einer PDF
  zusammenführen“, `#selbar`/`mergeSelected()` – unten rechts bleibt NUR der Speichern-Knopf, Tims
  UX-Regel). Baut per pdf-lib eine PDF aus allen markierten Dateien in Listenreihenfolge; JPG/PNG
  werden als Seiten eingebettet (`embedJpg`/`embedPng`). Quellen bleiben in der Liste, werden abgewählt
  und zeigen `mergedInto` („Zusammengeführt in …“). Hatten die Quellen verschiedene SICHERE Typen, wird
  das Ergebnis `typeSure=false` (gelb) statt still nach einer Datei benannt. „Verwerfen“ entfernt eine
  erzeugte Zeile (und die mergedInto-Vermerke). Erzeugte Dateien (`item.data`) werden beim Speichern
  immer neu geschrieben, Protokoll-Spalte „Hinweis“ nennt die Herkunft (Seiten/Quelldateien).
- **Speichern (EIN fester Weg, keine Modi):** Kopien nach `umbenannt/<Nachname_Vorname>/…` (auch als
  Pfade in der ZIP – je Person ein Ordner fürs Ziehen in die eAkte), Originale unverändert nach
  `verarbeitet/`. Nie überschreiben (`uniqueName` hängt `_2` an, je Zielordner eigene Namensliste),
  Fremddateien unberührt, immer `Protokoll_<Zeit>.csv` in `umbenannt/` (UTF-8 mit BOM, Semikolon →
  Excel-tauglich; Spalte „Neuer Name“ enthält den Unterordner-Pfad). Die ZIP ist NUR der Notweg ohne
  Ordnerzugriff.
- **Mehrkunden/Dauerbetrieb:** Ohne Vorgabe wird der Name je Dokument erkannt → mehrere Personen in
  einem Durchlauf. „Neue Dateien einlesen“ (`rescanFolder()`): entfernt erledigte (applied) Zeilen,
  liest nur Dateien nach, die weder in der Liste noch in `state.done` stehen. `start(items, append)`
  hängt neue Dateien an, statt die Liste zu ersetzen. **Der Scan-Ordner ist die Wahrheit:** Das
  Original wandert nach dem Speichern in den Unterordner `verarbeitet/`
  (Vorher-Check per `state.dir.resolve(handle)`, damit nichts doppelt verschoben wird; scheitert das
  Verschieben, bleibt die Zeile trotzdem „applied“). Dadurch überlebt der Arbeitsstand jeden
  Browser-Neustart OHNE persistenten Speicher – `state.done` lebt bewusst nur im Arbeitsspeicher,
  denn Dateinamen sind Personendaten und dürfen nie in localStorage (Regel 2/localStorage-Regel).
  Zurückholen = Datei im Explorer aus `verarbeitet/` zurückziehen.
- **Stammordner:** Der erste Ordner (gewählt oder gezogen) ist der Stammordner (`state.dir`). Danach
  gezogene Dateien/Ordner ERGÄNZEN die Liste (`pickFiles` append, `addExternalDir` liest fremde Ordner
  nur aus): `it.extern`, `partInfo` „Per Drag & Drop hinzugefügt“, Duplikat-Schutz über Liste +
  `state.done`. Beim Speichern werden externe Dateien (kein `it.handle`) in den Stammordner
  geschrieben („In den Ordner übernommen“); fremde Originale/Ordner werden NIE verändert.
  „Ordner wählen“ wechselt den Stammordner (ersetzt die Liste).
- **Bedienung:** Drag & Drop von Dateien oder einem Ordner aufs Fenster (`initDrop()`; ein Ordner kommt
  per `getAsFileSystemHandle` in den echten Ordnermodus). Filter „Nur zu prüfende anzeigen“
  (`applyRowFilter`, bewusst nur beim Neuzeichnen, damit Zeilen nicht beim Tippen verschwinden).
  „Erkennungsregeln“ (Kopfzeile) öffnet die Read-only-Ansicht aller Typen/Begriffe (`openRules()`).
- **localStorage** nur für Programmeinstellungen (derzeit nur das Dateinamen-Muster). Nie Namen oder
  Inhalte speichern.

## Fallstricke (alle schon einmal gelöst – nicht wieder einbauen)

- **file:// ist ein „opaker“ Ursprung.** fetch(), ES-Module (`type="module"`) und Schriften per `url()`
  funktionieren dort nicht. Deshalb: Bibliotheken als `<script src>`, Binärdaten als Base64 in .js-Dateien,
  Schriften als data:-URLs in `lib/fonts.css`.
- **Tesseract-Worker darf nichts nachladen** (importScripts eines blob: aus dem Hauptfenster schlägt fehl).
  Lösung in `ocr()`: Sprachdaten (Base64) + fetch-Ersatz + Tesseract-Kern + Worker-Code werden zu EINEM
  Blob zusammengesetzt. `corePath` ist dann egal, weil `TesseractCore` schon global existiert.
- **Bug in tesseract.js 5.1.1:** Sprachdaten als Objekt `{code, data}` übergeben → `initialize` reicht die
  Daten statt des Codes weiter („Failed loading language '31,139,8,…'“). Deshalb wird `"deu"` als Text
  übergeben und der fetch im Worker auf die eingebetteten Daten umgebogen. Bei einem Tesseract-Update prüfen,
  ob der Bug behoben ist.
- **pdf.js ab 4.x** gibt es nur als ES-Modul → unter file:// unbrauchbar. Bei 3.11.174 bleiben. Der
  pdf.js-Worker läuft als „fake worker“ im Hauptthread (`lib/pdf.worker.min.js` per Script geladen).
- **Ohne Zeitlimit hängt die Texterkennung stumm**, wenn der Worker scheitert. `withTimeout()` +
  `errorHandler` beibehalten, damit eine klare Fehlermeldung kommt.
- **OCR liefert Leerzeilen** zwischen Anrede und Name → Muster müssen `\s*` über Zeilenumbrüche erlauben.
- **.bat-Dateien:** nur ASCII (keine Umlaute), CRLF-Zeilenenden, sonst funktionieren Sprungmarken nicht.
- **Edge-Gruppenrichtlinien** können den Ordnerzugriff sperren. Dann fällt das Programm automatisch auf
  Dateiauswahl + ZIP-Download zurück. Diesen Ersatzweg nicht entfernen.
- **SVG-Logo aus marke.js** wird per DOMParser eingefügt, `<script>`/`foreignObject` werden entfernt.

## Testen

```bash
python3 -m pip install playwright pillow reportlab pypdf   # einmalig; unter Python 3.9: "reportlab<4.4"
python3 -m playwright install chromium                      # einmalig
bash tests/alle_tests.sh                                     # alle Tests (ca. 2–3 Minuten)
python3 tests/test_dateimodus.py                             # einzelner Test
```

| Test | Prüft |
| --- | --- |
| test_dateimodus.py | Typ + Name aller Testunterlagen ohne und mit Vorgabe; manuelle Korrektur; ZIP-Export |
| test_namen.py | findName direkt auf Textproben (zwei Vornamen, Formular-Tabellen, beschriftete Felder, Absender, Anrede) |
| test_regeln.py | classify auf Textproben (neue Praxis-Typen + Regressionen), Drag & Drop, Filter, Regeln-Dialog |
| test_teilen.py | Stapel-Scan: Mehrtyp-Hinweis, Trennvorschlag, leere Seite erkannt/weggelassen, Trennstelle von Hand, Teilen, ZIP + Protokoll-Hinweis; Zusammenführen PDF+JPG, Verwerfen |
| test_drehen.py | Verdrehter Scan (tests/testdocs/extra/) wird erkannt + gerade gespeichert (pypdf prüft /Rotate), „Seite drehen“ von Hand, Vorschau im Ordnermodus, Zoom liegt ÜBER dem Dialog, pagesRead/pageTexts neu erzeugter Dateien |
| test_mehrkunden.py | Unterordner je Person (Ordner + ZIP), „Neue Dateien einlesen“, Stammordner (zugezogene Dateien ergänzen + landen im Ordner) |
| test_ordnermodus.py | Standard-Ablage: umbenannt/<Person>/, Originale nach verarbeitet/, Ersatzweg ohne move(), keine Überschreibung, Fremddateien, Neustart liest nichts doppelt |
| test_offline.py | läuft ohne Netz, null Netzanfragen |
| test_ci.py | Farben/Name aus marke.js, Schriften offline, Logo-Einbau sicher; Screenshots in tests/screenshots |

Neue Testunterlagen: in `tests/testdocs_erzeugen.py` ergänzen (fiktiv!), Skript ausführen, Erwartungswerte in
`test_dateimodus.py` (TYP, PERS) eintragen. Screenshots nach UI-Änderungen ansehen (hell und dunkel).

Manuell vor jeder Auslieferung: einmal auf einem echten Windows-PC mit Edge starten, „Ordner wählen“ mit den
Beispiel-Scans durchspielen (der echte Ordner-Dialog lässt sich nicht automatisiert testen).

## Ausliefern

`bash tools/release_bauen.sh` → führt alle Tests aus, setzt CRLF, prüft .bat auf ASCII, kopiert die
Beispiel-Scans und erstellt `dist/Unterlagen-Sortierer_<VERSION>.zip`. Vorher `VERSION` hochzählen.

## Kunden-Varianten

Anderes Design: nur `marke.js` tauschen. Andere Dokumenttypen: nur `regeln.js`. Das Programm selbst bleibt
für alle Kunden gleich. Kundenspezifische Dateien nicht in dieses Repo einchecken, sondern getrennt ablegen.

## Offene Punkte

- [x] Orgalytics-Bildmarke in `marke.js` eingesetzt (06.11.2026)
- [ ] Erster Test auf echtem Windows-PC mit Edge und auf einem Mac (Doppelklick auf die .command)
- [ ] Regeln mit echten (anonymisierten) Kundenbeispielen schärfen
