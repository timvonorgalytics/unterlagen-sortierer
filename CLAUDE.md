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
  Unterlagen-Sortierer starten.bat   Start in Edge → Chrome → Standardbrowser (nur ASCII, CRLF!)
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
  („Name, Vorname:“, „Nachname:“, „Name:“ + „Vorname:“ auf Ausweisen) → Anschrift („Herrn/Frau“, auch allein
  in einer Zeile mit Leerzeilen danach, „Herrn und Frau Hans und Erika …“). Zeilen mit Ansprechpartner,
  Sachbearbeiter, Vermieter usw. (`NOT_PERSON`) und Namen direkt über „- Vermieter -“ werden übersprungen.
- **Manuelle Änderungen** stehen in `item.manual` und werden beim Neu-Auswerten nicht überschrieben.
- **Speichern:** nie überschreiben (`uniqueName` hängt `_2` an), Fremddateien im Ordner unberührt lassen,
  immer `Protokoll_<Zeit>.csv` (UTF-8 mit BOM, Semikolon → Excel-tauglich).
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
python3 -m pip install playwright pillow reportlab   # einmalig
python3 -m playwright install chromium                # einmalig
bash tests/alle_tests.sh                               # alle Tests (ca. 1–2 Minuten)
python3 tests/test_dateimodus.py                       # einzelner Test
```

| Test | Prüft |
| --- | --- |
| test_dateimodus.py | Typ + Name aller Testunterlagen ohne Vorgabe, mit Vorgabe, mit Personenliste; manuelle Korrektur; ZIP-Export |
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
- [ ] Erster Test auf echtem Windows-PC mit Edge
- [ ] Regeln mit echten (anonymisierten) Kundenbeispielen schärfen
