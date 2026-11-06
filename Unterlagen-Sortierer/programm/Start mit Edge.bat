@echo off
rem Oeffnet den Unterlagen-Sortierer gezielt in Microsoft Edge (Ersatz: Chrome).
rem Normalerweise genuegt ein Doppelklick auf "Unterlagen-Sortierer.html" im Ordner darueber.
set "APP=%~dp0..\Unterlagen-Sortierer.html"
start "" msedge "%APP%" 2>nul && exit /b 0
start "" chrome "%APP%" 2>nul && exit /b 0
start "" "%APP%"
