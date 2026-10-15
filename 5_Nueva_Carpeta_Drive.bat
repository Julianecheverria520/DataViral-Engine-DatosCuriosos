@echo off
title InsightdataMind - Nueva carpeta en Drive
call venv\Scripts\activate
set /p tema="Tema del video: "
set /p canal="Canal (misterio, datos, espacio...): "
python -m core.tools.drive_watcher --nuevo "%tema%" --canal "%canal%"
pause
