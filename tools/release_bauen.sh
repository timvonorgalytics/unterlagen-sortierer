#!/usr/bin/env bash
# Erstellt das Auslieferungs-ZIP in dist/ – nur wenn alle Tests bestehen.
# Aufruf: tools/release_bauen.sh  [--ohne-tests]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
VERSION="$(tr -d '[:space:]' < VERSION)"
PROG="Unterlagen-Sortierer"

if [ "${1:-}" != "--ohne-tests" ]; then bash tests/alle_tests.sh; fi

# Windows-Dateien: CRLF; .bat nur ASCII (cmd liest sonst Umlaute falsch)
for f in "$PROG"/*.bat "$PROG"/*.txt "$PROG"/*.js "$PROG"/Beispiel-Scans/*.csv; do
  [ -f "$f" ] || continue
  perl -pi -e 's/\r?\n/\r\n/' "$f"
done
if LC_ALL=C grep -n '[^[:print:][:space:]]' "$PROG"/*.bat; then echo "FEHLER: Nicht-ASCII-Zeichen in .bat"; exit 1; fi

# macOS-Starter: LF-Zeilenenden und ausführbar (der Exec-Bit bleibt im ZIP erhalten)
for f in "$PROG"/*.command; do
  [ -f "$f" ] || continue
  perl -pi -e 's/\r\n/\n/' "$f"
  chmod +x "$f"
done

# Beispiel-Scans aktuell halten
mkdir -p "$PROG/Beispiel-Scans"
cp tests/testdocs/*.pdf tests/testdocs/*.jpg "$PROG/Beispiel-Scans/"

mkdir -p dist; OUT="dist/${PROG}_${VERSION}.zip"; rm -f "$OUT"
zip -rqX "$OUT" "$PROG" -x '*.DS_Store'
unzip -tq "$OUT" >/dev/null && echo "Fertig: $OUT ($(du -h "$OUT" | cut -f1))"
