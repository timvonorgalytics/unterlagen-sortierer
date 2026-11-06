# Unterlagen-Sortierer – Entwicklungsprojekt

Offline-Programm, das eingescannte Antragsunterlagen erkennt, klassifiziert und einheitlich umbenennt.
Alle Details für die Weiterentwicklung stehen in **CLAUDE.md**.

## Loslegen mit Claude Code

1. Diesen Ordner nach `~/ai-project/unterlagen-sortierer` entpacken.
2. In Claude Code (Desktop-App, Tab „Code“) den Ordner öffnen.
3. Als erste Aufgabe z. B.: „Lies CLAUDE.md, richte die Testumgebung ein und lass alle Tests laufen.“

## Wichtigste Befehle

| Was | Befehl |
| --- | --- |
| Alle Tests | `bash tests/alle_tests.sh` |
| Auslieferungs-ZIP bauen | `bash tools/release_bauen.sh` |
| Bibliotheken neu bauen | `bash tools/bibliotheken_bauen.sh` |
| Programm ansehen | `open Unterlagen-Sortierer/app/index.html` |
