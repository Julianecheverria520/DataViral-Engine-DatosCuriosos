@echo off
title InsightdataMind - Fase A: Preparar
call venv\Scripts\activate
set /p tema="Introduce el tema del video: "
echo Generando Guion, Audio e Imagenes para: %tema%
python main.py PREPARAR "%tema%"
pause