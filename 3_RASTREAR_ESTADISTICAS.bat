@echo off
title InsightdataMind - Estadisticas del canal
call venv\Scripts\activate
echo --- CONSULTANDO RENDIMIENTO DEL CANAL DE YOUTUBE ---
python main.py STATS
pause
