@echo off
title InsightdataMind - Vigilante de Google Drive
call venv\Scripts\activate
echo Vigilando tu carpeta de Drive. Deja esta ventana abierta.
echo Cada carpeta completa (guion + imagenes) se convierte en video automaticamente.
python -m core.tools.drive_watcher
pause
