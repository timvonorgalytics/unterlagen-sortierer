#!/bin/bash
# Oeffnet den Unterlagen-Sortierer gezielt in Chrome bzw. Edge (koennen Ordner direkt bearbeiten).
# Ein Doppelklick auf "Unterlagen-Sortierer.html" im Ordner darueber oeffnet den Standardbrowser;
# Safari speichert die Ergebnisse dann als ZIP-Datei statt direkt im Ordner.
DIR="$(cd "$(dirname "$0")/.." && pwd)"
APP="$DIR/Unterlagen-Sortierer.html"
open -a "Google Chrome" "$APP" 2>/dev/null && exit 0
open -a "Microsoft Edge" "$APP" 2>/dev/null && exit 0
open "$APP"
