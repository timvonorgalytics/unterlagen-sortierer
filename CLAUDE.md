# Unterlagen-Sortierer

Offline-Programm für Verwaltungen (Sozialamt, Grundsicherung): liest eingescannte Unterlagen (PDF/JPG/PNG)
aus einem Ordner, erkennt Dokumenttyp und Person und benennt die Dateien nach Muster um
(`Mustermann_Erika_Kontoauszug.pdf`). Betreiber: Orgalytics. Kunden: Windows-PCs mit Edge, oft ohne
Adminrechte. Ausgeliefert als ZIP, Start per Doppelklick auf eine .bat.

## Unverhandelbare Regeln

1. **Komplett offline.** Keine CDN-Links, kein fetch() ins Netz, keine Telemetrie. `tests/test_offline.py`
   prüft, dass keine einzige Netzanfrage entsteht. Das ist das zentrale Datenschutzversprechen.
2. **Keine echten Bürgerdaten** in diesem Projekt oder in Prompts. Nur fiktive/anonymisierte Testunterlagen
   (`tests/testdocs`, Personen „Mustermann“). Echte Problemfälle vom Kunden nur anonymisiert nachbauen.
3. **Vor jeder Übergabe `tests/alle_tests.sh`** – alle Tests müssen bestehen. Neue Funktion = neuer Test.
4. **CI nur über `Unterlagen-Sortierer/marke.js`.** Keine Markenwerte (Farben, Namen, Logo) in index.html
   hart kodieren. Quelle der Orgalytics-Werte: die internen Markenvorlagen. Nie Farben oder Texte raten.
5. **Kein Build-Schritt für Kunden.** Das Programm muss als entpackter Ordner per file:// laufen.
6. Oberfläche und Texte auf Deutsch, Satzanfang groß, aktive Verben („Dateien umbenennen“, nicht „Absenden“).

## Aufbau

```
Unterlagen-Sortierer/            ← das Auslieferungsprodukt (wird gezippt)
  Unterlagen-Sortierer starten.bat       Windows: Start in Edge → Chrome → Standardbrowser (nur ASCII, CRLF!)
  Unterlagen-Sortierer starten.command   macOS: Start in Chrome → Edge → Standardbrowser (LF, ausführbar!)
  regeln.js        Dokumenttypen + Suchbegriffe (vom Kunden-IT editierbar)  → window.REGELN
  marke.js         Name, Farben, Logo-SVG, Fußzeile                         → window.MARKE
  LIESMICH.txt, Hinweise fuer die IT.txt
  Beispiel-Scans/  (wird von tools/release_bauen.sh aus tests/testdocs befüllt)
  app/index.html   gesamte Oberfläche + Logik (ein File, kein Framework)
  app/lib/         gebaute Bibliotheken – NICHT von Hand ändern, nur via tools/bibliotheken_bauen.sh
tests/             Playwright-Tests (Python) + fiktive Testunterlagen
tools/             bibliotheken_bauen.sh, release_bauen.sh
VERSION            Versionsnummer für das Release-ZIP
```

### Ablauf in app/index.html

`pickFolder()`/`pickFiles()` → `start()` (parallel, Anzahl = halbe Kerne, max. 3) → `readText()`
(PDF: Textebene per pdf.js, sonst Seite rendern → Tesseract; Bilder → Tesseract) → `analyse()`
= `classify()` + `findName()` + `findDate()` → Tabelle → `apply()` → `applyFolder()` (Ordnerzugriff)
oder `applyZip()` (Ersatz ohne Ordnerzugriff, eigener ZIP-Schreiber ohne Kompression).

- **classify:** Begriffe aus regeln.js, normalisiert (`norm()`: klein, ä→ae, ß→ss, nur a-z0-9).
  `stark` = 3 Punkte, `schwach` = 1; im Kopf der Seite (erste 450 Zeichen) ×1,5.
  „Sicher“ wenn ≥ 3 Punkte und ≥ 1,5× der Zweitplatzierte.
- **findName (Reihenfolge):** Personenliste (CSV) → Vorgabe aus den Eingabefeldern → Formularfelder
  („Name, Vorname:“; „Familienname/Nachname“ und „Vorname(n)“ auch mit Wert in der NÄCHSTEN Zeile
  (Formular-Tabellen) und mit zwei Vornamen; beschriftete Voll-Namen-Felder Mieter(in)/Patient(in)/
  Kontoinhaber(in)/Versicherungsnehmer(in)) → Anschrift („Herrn/Frau“, auch allein in einer Zeile mit
  Leerzeilen danach, „Herrn und Frau Hans und Erika …“, zwei Vornamen „Frau Helga Maria Brandt“ →
  letztes Wort = Nachname, außer es ist eine Straße) → Absenderblock (Namenszeile direkt über
  „Straße + Hausnummer“, keine Firmen/Behörden via `ORGA`) → Briefanrede („Sehr geehrte Frau X“, nur
  Nachname). Zeilen mit Ansprechpartner, Sachbearbeiter, Vermieter usw. (`NOT_PERSON`) und Namen direkt
  über „- Vermieter -“ werden übersprungen; `FELDWORT` verhindert, dass Beschriftungen („Vorname“,
  „Geburtsdatum“) als Namen durchgehen. Quellen-Vertrauen: Formularfeld sicher, Anschrift/Absender/
  Anrede unsicher („Bitte prüfen“). Fälle in `tests/test_namen.py` (direkt auf findName, ohne OCR).
- **Manuelle Änderungen** stehen in `item.manual` und werden beim Neu-Auswerten nicht überschrieben.
- **Teilen (Stapel-Scans):** Jede mehrseitige PDF hat „Teilen …“ → `openSplit()` liest ALLE Seiten
  (Textebene, sonst OCR), klassifiziert jede Seite und schlägt Trennstellen vor (`proposeCuts`: neuer
  Abschnitt, sobald eine Seite *sicher* einen anderen Typ hat; unsichere Seiten bleiben beim Abschnitt).
  Trennstellen per Klick änderbar. `doSplit()` erzeugt per **pdf-lib** je Abschnitt eine neue PDF als
  Tabellenzeile (`item.data` = Bytes, `item.derived`, `item.partInfo`); das Original bleibt unverändert
  und wird abgewählt. `analyse()` setzt `item.multiHint`, wenn die gelesenen Seiten sicher verschiedene
  Typen haben → gelber Hinweis in der Typ-Spalte.
- **Zusammenführen:** „Markierte zusammenführen“ (`mergeSelected()`, sichtbar ab 2 markierten Zeilen)
  baut per pdf-lib eine PDF aus allen markierten Dateien in Listenreihenfolge; JPG/PNG werden als Seiten
  eingebettet (`embedJpg`/`embedPng`). Originale bleiben, werden abgewählt. „Verwerfen“ entfernt eine
  erzeugte Zeile wieder. Erzeugte Dateien (`item.data`) werden beim Speichern immer neu geschrieben
  (auch im Modus „umbenennen“), Protokoll-Spalte „Hinweis“ nennt die Herkunft (Seiten/Quelldateien).
- **Speichern:** nie überschreiben (`uniqueName` hängt `_2` an, je Zielordner eigene Namensliste),
  Fremddateien im Ordner unberührt lassen, immer `Protokoll_<Zeit>.csv` im Haupt-Zielordner (UTF-8 mit
  BOM, Semikolon → Excel-tauglich; Spalte „Neuer Name“ enthält ggf. den Unterordner-Pfad).
  Haken „Je Person einen Unterordner anlegen“ (`#perperson`): Dateien landen in `Nachname_Vorname/`
  (auch als Pfade in der ZIP) – für das Ziehen pro Person in die eAkte. Die eAkte nimmt einzelne
  Dateien per Drag & Drop an; die ZIP ist NUR der Notweg ohne Ordnerzugriff.
- **Mehrkunden/Dauerbetrieb:** Ohne Vorgabe wird der Name je Dokument erkannt → mehrere Personen in
  einem Durchlauf. „Neue Dateien einlesen“ (`rescanFolder()`): entfernt erledigte (applied) Zeilen,
  liest nur Dateien nach, die weder in der Liste noch in `state.done` stehen. `start(items, append)`
  hängt neue Dateien an, statt die Liste zu ersetzen. **Der Scan-Ordner ist die Wahrheit:** Im
  Kopien-Modus wandert das Original nach dem Speichern in den Unterordner `verarbeitet/`
  (Vorher-Check per `state.dir.resolve(handle)`, damit nichts doppelt verschoben wird; scheitert das
  Verschieben, bleibt die Zeile trotzdem „applied“). Dadurch überlebt der Arbeitsstand jeden
  Browser-Neustart OHNE persistenten Speicher – `state.done` lebt bewusst nur im Arbeitsspeicher,
  denn Dateinamen sind Personendaten und dürfen nie in localStorage (Regel 2/localStorage-Regel).
  Zurückholen = Datei im Explorer aus `verarbeitet/` zurückziehen.
- **Bedienung:** Drag & Drop von Dateien oder einem Ordner aufs Fenster (`initDrop()`; ein Ordner kommt
  per `getAsFileSystemHandle` in den echten Ordnermodus). Filter „Nur zu prüfende anzeigen“
  (`applyRowFilter`, bewusst nur beim Neuzeichnen, damit Zeilen nicht beim Tippen verschwinden).
  „Erkennungsregeln“ (Kopfzeile) öffnet die Read-only-Ansicht aller Typen/Begriffe (`openRules()`).
- **localStorage** nur für Programmeinstellungen (Muster, Ablage, Seiten). Nie Namen oder Inhalte speichern.

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
python3 -m pip install playwright pillow reportlab   # einmalig; unter Python 3.9: "reportlab<4.4"
python3 -m playwright install chromium                # einmalig
bash tests/alle_tests.sh                               # alle Tests (ca. 1–2 Minuten)
python3 tests/test_dateimodus.py                       # einzelner Test
```

| Test | Prüft |
| --- | --- |
| test_dateimodus.py | Typ + Name aller Testunterlagen ohne Vorgabe, mit Vorgabe, mit Personenliste; manuelle Korrektur; ZIP-Export |
| test_namen.py | findName direkt auf Textproben (zwei Vornamen, Formular-Tabellen, beschriftete Felder, Absender, Anrede) |
| test_regeln.py | classify auf Textproben (neue Praxis-Typen + Regressionen), Drag & Drop, Filter, Regeln-Dialog |
| test_teilen.py | Stapel-Scan: Mehrtyp-Hinweis, Trennvorschlag, leere Seite erkannt/weggelassen, Trennstelle von Hand, Teilen, ZIP + Protokoll-Hinweis; Zusammenführen PDF+JPG, Verwerfen |
| test_mehrkunden.py | Unterordner je Person (Ordner- und ZIP-Modus), „Neue Dateien einlesen“ (erledigte raus, nur Neue dazu, nichts doppelt) |
| test_ordnermodus.py | Kopien in „umbenannt“, Originale umbenennen, Ersatzweg ohne move(), keine Überschreibung, Fremddateien |
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

- [ ] Orgalytics-Bildmarke in `marke.js` einsetzen
- [ ] Erster Test auf echtem Windows-PC mit Edge und auf einem Mac (Doppelklick auf die .command)
- [ ] Regeln mit echten (anonymisierten) Kundenbeispielen schärfen
