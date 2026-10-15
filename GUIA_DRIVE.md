# Videos desde Google Drive (sin costos de API)

Las imágenes las sigues creando y aprobando tú en Gemini. El motor solo pone la voz (edge-tts, gratis) y monta el video.

## Configuración (una sola vez)
1. Instala **Google Drive para escritorio** y crea en tu Drive una carpeta, por ejemplo `DataViral`.
2. En el `.env` del proyecto agrega la ruta como la ve tu PC:
   ```
   DRIVE_DIR=G:\Mi unidad\DataViral
   ```
3. Abre `4_Vigilar_Drive.bat` y déjalo abierto. Revisa la carpeta cada minuto.

## Cada video
1. Crea una subcarpeta por video dentro de `DataViral` (o usa `5_Nueva_Carpeta_Drive.bat`, que la crea con una plantilla).
2. Pon dentro un `guion.txt`: un párrafo por escena, separados por una línea en blanco. Arriba puedes poner:
   ```
   # canal: misterio
   # titulo: Título para redes
   # hashtags: #datoscuriosos #viral
   ```
   Las líneas con `#` o que empiezan por `Prompt:` se ignoran, así que puedes dejar ahí los prompts de Gemini.
   También sirve el `guion.json` que genera `PREPARAR` (y si copias su `audio.mp3` y `timestamps.json`, se reutilizan).
3. Sube las imágenes aprobadas numeradas: `1.png`, `2.png`, ... (también vale `img_1.jpg` o `escena 1.png`). Una por escena.
4. Cuando hay una imagen por escena y nada ha cambiado en 60 s, se genera el video y aparece en la misma carpeta junto con `info_publicacion.txt` y `VIDEO_LISTO.txt`.

Si algo falla verás un `ERROR.txt` en la carpeta con el motivo. Bórralo para reintentar. Para regenerar un video, borra `VIDEO_LISTO.txt`.
Las carpetas que empiezan por `_` se ignoran (útil para borradores).
