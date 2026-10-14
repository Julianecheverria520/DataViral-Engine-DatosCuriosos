# Subida automática a YouTube

Paso opcional que sube a YouTube los videos ya montados en `output/videos/`, usando el título y los hashtags de `proyectos/<tema>/info_publicacion.txt`.

Flujo completo:

1. `1_Preparar_Recursos.bat` → guion, audio, imágenes e `info_publicacion.txt`
2. `2_Montar_Video.bat` → `output/videos/<tema>_Final.mp4`
3. **`4_Subir_YouTube.bat`** → sube los videos que todavía no se han subido

Puedes editar `info_publicacion.txt` antes de subir; el script usa lo que haya ahí. Si el archivo falta, toma `titulo_redes` y `hashtags` de `guion.json`.

## Configuración (una sola vez)

### 1. Instalar las librerías

```bat
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Crear las credenciales OAuth en Google Cloud

1. Entra a <https://console.cloud.google.com/> y crea un proyecto (por ejemplo `InsightdataMind`).
2. **APIs y servicios → Biblioteca** → busca **YouTube Data API v3** → **Habilitar**.
3. **APIs y servicios → Pantalla de consentimiento de OAuth**:
   - Tipo de usuario: **Externo**.
   - Rellena nombre de la app y tu correo.
   - En **Usuarios de prueba**, agrega la cuenta de Google dueña del canal.
4. **APIs y servicios → Credenciales → Crear credenciales → ID de cliente de OAuth**:
   - Tipo de aplicación: **App de escritorio**.
   - Descarga el JSON.
5. Guarda ese archivo como:

```
credentials/client_secret.json
```

La carpeta `credentials/` está en `.gitignore`; nunca la subas al repositorio ni la compartas.

### 3. Autorizar el canal

La primera vez que ejecutes la subida se abrirá el navegador para que inicies sesión con la cuenta del canal y aceptes el permiso. Después se guarda `credentials/youtube_token.json` y ya no te lo vuelve a pedir.

Si tu cuenta maneja varios canales, elige el canal correcto en esa pantalla.

## Uso

```bat
4_Subir_YouTube.bat
```

o desde la terminal:

```bat
python main.py SUBIR                       :: sube todo lo pendiente como privado
python main.py SUBIR public                :: sube como público
python main.py SUBIR unlisted              :: sube como oculto
python main.py SUBIR --simular             :: muestra qué subiría, sin subir nada
python main.py SUBIR public --proyecto Pulpos_35s   :: solo ese proyecto
```

La privacidad por defecto es `private`, para que revises el video en YouTube Studio antes de publicarlo.

Cuando un video se sube, se crea `proyectos/<tema>/youtube_subido.json` con el ID y el enlace. Los proyectos con ese archivo se saltan en las siguientes ejecuciones; bórralo si quieres volver a subir ese video.

## Qué se envía a YouTube

- **Título**: la línea bajo `TITULO PARA REDES:` (máx. 100 caracteres).
- **Descripción**: el título + los hashtags.
- **Etiquetas**: los hashtags sin `#`.
- Se añade `#Shorts` si no estaba.
- Categoría: Educación. Idioma: español. No es contenido para niños.

## Límites a tener en cuenta

- **Apps sin verificar quedan en privado**: mientras tu proyecto de Google Cloud no pase la auditoría de la YouTube API, YouTube bloquea como *privado* todo lo que se suba por API, aunque pidas `public`. Puedes publicarlo a mano desde YouTube Studio o solicitar la auditoría en <https://support.google.com/youtube/contact/yt_api_form>.
- **Cuota diaria**: la cuota gratuita es de 10.000 unidades por día y cada subida cuesta unas 1.600, así que caben unos 6 videos al día.
- **Token caducado**: con la pantalla de consentimiento en modo *Prueba*, Google invalida el token cada 7 días. Si ves un error de autorización, borra `credentials/youtube_token.json` y vuelve a autorizar.
