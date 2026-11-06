#!/bin/bash
# Startet den Unterlagen-Sortierer (macOS). Reihenfolge: Chrome -> Edge -> Standardbrowser.
# Chrome und Edge koennen Ordner direkt bearbeiten; Safari speichert stattdessen eine ZIP-Datei.
DIR="$(cd "$(dirname "$0")" && pwd)"
APP="$DIR/app/index.html"
open -a "Google Chrome" "$APP" 2>/dev/null && exit 0
open -a "Microsoft Edge" "$APP" 2>/dev/null && exit 0
open "$APP"
