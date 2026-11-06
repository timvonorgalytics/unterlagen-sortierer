#!/usr/bin/env bash
# Baut Unterlagen-Sortierer/app/lib neu aus npm-Paketen (feste Versionen).
# Nur nötig, wenn eine Bibliothek aktualisiert werden soll. Danach: tests/alle_tests.sh
#
# Warum Base64 in .js-Dateien? Das Programm läuft als file:// – dort sind fetch(),
# ES-Module und Schriften per url() gesperrt. <script src> und data:-URLs funktionieren.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LIB="$ROOT/Unterlagen-Sortierer/app/lib"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT

TESSERACT=5.1.1          # Achtung: Workaround für Sprachdaten-Bug in index.html (siehe CLAUDE.md)
PDFJS=3.11.174           # letzte Version mit UMD-Build (ab 4.x nur ES-Module → file:// geht nicht)
PDFLIB=1.17.1            # pdf-lib: PDFs schreiben (Teilen/Zusammenführen), UMD-Build
DEU=1.0.0                # @tesseract.js-data/deu, Modell 4.0.0_best_int
GEIST=1.3.1
LORA=5.1.0

cd "$TMP"; npm init -y >/dev/null
npm i --silent "tesseract.js@$TESSERACT" "pdfjs-dist@$PDFJS" "pdf-lib@$PDFLIB" "@tesseract.js-data/deu@$DEU" "geist@$GEIST" "@fontsource-variable/lora@$LORA"
N="$TMP/node_modules"
b64js() { printf 'window.%s="' "$1" > "$3"; base64 < "$2" | tr -d '\n' >> "$3"; printf '";\n' >> "$3"; }

mkdir -p "$LIB/lizenzen"
cp "$N/pdfjs-dist/build/pdf.min.js" "$N/pdfjs-dist/build/pdf.worker.min.js" "$N/tesseract.js/dist/tesseract.min.js" "$LIB/"
cp "$N/pdf-lib/dist/pdf-lib.min.js" "$LIB/"
b64js TESS_WORKER_B64     "$N/tesseract.js/dist/worker.min.js"                      "$LIB/tess-worker.js"
b64js TESS_CORE_SIMD_B64  "$N/tesseract.js-core/tesseract-core-simd-lstm.wasm.js"   "$LIB/tess-core-simd.js"
b64js TESS_CORE_B64       "$N/tesseract.js-core/tesseract-core-lstm.wasm.js"        "$LIB/tess-core.js"
b64js TESS_DEU_B64        "$N/@tesseract.js-data/deu/4.0.0_best_int/deu.traineddata.gz" "$LIB/deu.js"
{
  printf '/* Geist (Vercel) und Lora (Cyreal) – SIL Open Font License 1.1 – eingebettet für den Offline-Betrieb */\n'
  printf '@font-face{font-family:"Geist";font-style:normal;font-weight:100 900;font-display:swap;src:url(data:font/woff2;base64,'
  base64 < "$N/geist/dist/fonts/geist-sans/Geist-Variable.woff2" | tr -d '\n'; printf ') format("woff2");}\n'
  printf '@font-face{font-family:"Lora";font-style:normal;font-weight:400 700;font-display:swap;src:url(data:font/woff2;base64,'
  base64 < "$N/@fontsource-variable/lora/files/lora-latin-wght-normal.woff2" | tr -d '\n'; printf ') format("woff2");}\n'
} > "$LIB/fonts.css"
cp "$N/tesseract.js/LICENSE.md" "$LIB/lizenzen/tesseract.js-LICENSE.txt"
cp "$N/tesseract.js-core/LICENSE" "$LIB/lizenzen/tesseract-core-LICENSE.txt"
cp "$N/pdfjs-dist/LICENSE" "$LIB/lizenzen/pdfjs-LICENSE.txt"
cp "$N/pdf-lib/LICENSE.md" "$LIB/lizenzen/pdf-lib-LICENSE.txt"
cp "$N/geist/LICENSE.TXT" "$LIB/lizenzen/geist-OFL.txt"
cp "$N/@fontsource-variable/lora/LICENSE" "$LIB/lizenzen/lora-OFL.txt"
echo "Bibliotheken neu gebaut in $LIB"
