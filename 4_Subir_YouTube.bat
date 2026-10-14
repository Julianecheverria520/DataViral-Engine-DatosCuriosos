@echo off
title InsightdataMind - Fase C: Subir a YouTube
call venv\Scripts\activate
echo Privacidad: private (solo tu), unlisted (oculto) o public
set /p priv="Privacidad [private]: "
if "%priv%"=="" set priv=private
python main.py SUBIR %priv%
pause
