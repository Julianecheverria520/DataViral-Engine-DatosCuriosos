@echo off
title InsightdataMind - Fase B: Montaje
call venv\Scripts\activate
echo Renderizando videos detectados en /proyectos/...
python main.py MONTAR
pause