@echo off
rem Startet den Unterlagen-Sortierer in Microsoft Edge (Ersatz: Chrome, dann Standardbrowser)
set "APP=%~dp0app\index.html"
start "" msedge "%APP%" 2>nul && exit /b 0
start "" chrome "%APP%" 2>nul && exit /b 0
start "" "%APP%"
