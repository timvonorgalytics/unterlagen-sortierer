#!/usr/bin/env bash
# Erstellt das Auslieferungs-ZIP in dist/ – nur wenn alle Tests bestehen.
# Aufruf: tools/release_bauen.sh  [--ohne-tests]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
VERSION="$(tr -d '[:space:]' < VERSION)"
PROG="Unterlagen-Sortierer"

# Version und Lizenz ins Produkt übernehmen
printf '// Wird von tools/release_bauen.sh aus der Datei VERSION erzeugt – nicht von Hand ändern.\nwindow.APP_VERSION = "%s";\n' "$VERSION" > "$PROG/programm/version.js"
cp LICENSE "$PROG/programm/Lizenz.txt"

if [ "${1:-}" != "--ohne-tests" ]; then bash tests/alle_tests.sh; fi

# Windows-Dateien: CRLF; .bat nur ASCII (cmd liest sonst Umlaute falsch)
for f in "$PROG"/programm/*.bat "$PROG"/programm/*.txt "$PROG"/programm/*.js "$PROG"/programm/Beispiel-Scans/*.csv; do
  [ -f "$f" ] || continue
  perl -pi -e 's/\r?\n/\r\n/' "$f"
done
if LC_ALL=C grep -n '[^[:print:][:space:]]' "$PROG"/programm/*.bat; then echo "FEHLER: Nicht-ASCII-Zeichen in .bat"; exit 1; fi

# macOS-Starter: LF-Zeilenenden und ausführbar (der Exec-Bit bleibt im ZIP erhalten)
for f in "$PROG"/programm/*.command; do
  [ -f "$f" ] || continue
  perl -pi -e 's/\r\n/\n/' "$f"
  chmod +x "$f"
done

# Oberste Ebene des Produkts: genau EINE Datei (Unterlagen-Sortierer.html)
anz=$(find "$PROG" -maxdepth 1 -type f ! -name '.DS_Store' | wc -l | tr -d ' ')
if [ "$anz" != "1" ]; then echo "FEHLER: Im Produktordner muss genau eine Datei liegen (gefunden: $anz)"; exit 1; fi

# Beispiel-Scans aktuell halten
mkdir -p "$PROG/programm/Beispiel-Scans"
cp tests/testdocs/*.pdf tests/testdocs/*.jpg "$PROG/programm/Beispiel-Scans/"

mkdir -p dist; OUT="dist/${PROG}_${VERSION}.zip"; rm -f "$OUT"
zip -rqX "$OUT" "$PROG" -x '*.DS_Store'
unzip -tq "$OUT" >/dev/null && echo "Fertig: $OUT ($(du -h "$OUT" | cut -f1))"
