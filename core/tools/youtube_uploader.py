"""
Subida automática de videos terminados a YouTube (YouTube Data API v3).

Lee cada proyecto de proyectos/<tema>/, busca su video final en
output/videos/<tema>_Final.mp4, toma título y hashtags de info_publicacion.txt
y lo sube. Deja una marca youtube_subido.json en la carpeta del proyecto
para no subirlo dos veces.

Credenciales (ver README_YOUTUBE.md):
  credentials/client_secret.json  -> descargado de Google Cloud Console
  credentials/youtube_token.json  -> se crea solo la primera vez que autorizas
"""
import json
import os
from datetime import datetime

BASE_DIR = "proyectos"
OUTPUT_DIR = os.path.join("output", "videos")
CREDENTIALS_DIR = "credentials"
CLIENT_SECRET = os.path.join(CREDENTIALS_DIR, "client_secret.json")
TOKEN_FILE = os.path.join(CREDENTIALS_DIR, "youtube_token.json")
MARCA_SUBIDO = "youtube_subido.json"

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CATEGORIA_EDUCACION = "27"
PRIVACIDADES = ("private", "unlisted", "public")


# ==========================================================
# METADATOS
# ==========================================================
def leer_info_publicacion(path_proyecto):
    """Devuelve (titulo, hashtags) a partir de info_publicacion.txt.
    Si falta, usa titulo_redes/hashtags de guion.json."""
    titulo, hashtags = None, []
    info_path = os.path.join(path_proyecto, "info_publicacion.txt")

    if os.path.exists(info_path):
        with open(info_path, "r", encoding="utf-8") as f:
            lineas = [l.strip() for l in f.read().splitlines()]
        seccion = None
        for linea in lineas:
            if linea.upper().startswith("TITULO PARA REDES"):
                seccion = "titulo"
                continue
            if linea.upper().startswith("HASHTAGS"):
                seccion = "hashtags"
                continue
            if not linea:
                continue
            if seccion == "titulo" and titulo is None:
                titulo = linea
            elif seccion == "hashtags":
                hashtags += [h for h in linea.split() if h.startswith("#")]

    guion_path = os.path.join(path_proyecto, "guion.json")
    if (not titulo or not hashtags) and os.path.exists(guion_path):
        with open(guion_path, "r", encoding="utf-8") as f:
            datos = json.load(f)
        titulo = titulo or datos.get("titulo_redes")
        hashtags = hashtags or list(datos.get("hashtags", []))

    if not titulo:
        titulo = os.path.basename(path_proyecto).replace("_", " ")
    return titulo, hashtags


def construir_metadatos(titulo, hashtags):
    """Arma el body de videos.insert respetando los límites de YouTube."""
    hashtags = [h if h.startswith("#") else f"#{h}" for h in hashtags]
    if "#shorts" not in [h.lower() for h in hashtags]:
        hashtags.append("#Shorts")

    # YouTube: título máx. 100 caracteres, sin < >
    titulo_limpio = titulo.replace("<", "").replace(">", "").strip()[:100]
    descripcion = f"{titulo_limpio}\n\n{' '.join(hashtags)}"
    tags = [h.lstrip("#") for h in hashtags]

    # Las etiquetas suman máx. ~500 caracteres en total
    tags_finales, total = [], 0
    for t in tags:
        if total + len(t) + 1 > 450:
            break
        tags_finales.append(t)
        total += len(t) + 1

    return {
        "snippet": {
            "title": titulo_limpio,
            "description": descripcion[:5000],
            "tags": tags_finales,
            "categoryId": CATEGORIA_EDUCACION,
            "defaultLanguage": "es",
            "defaultAudioLanguage": "es",
        },
        "status": {
            "selfDeclaredMadeForKids": False,
        },
    }


# ==========================================================
# AUTENTICACIÓN
# ==========================================================
def obtener_servicio_youtube():
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError:
        raise RuntimeError(
            "Faltan librerías de Google. Ejecuta:\n"
            "  pip install google-api-python-client google-auth-oauthlib google-auth-httplib2"
        )

    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CLIENT_SECRET):
                raise RuntimeError(
                    f"No se encontró {CLIENT_SECRET}. Sigue los pasos de README_YOUTUBE.md."
                )
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET, SCOPES)
            creds = flow.run_local_server(port=0)
        os.makedirs(CREDENTIALS_DIR, exist_ok=True)
        with open(TOKEN_FILE, "w", encoding="utf-8") as f:
            f.write(creds.to_json())

    return build("youtube", "v3", credentials=creds)


# ==========================================================
# SUBIDA
# ==========================================================
def subir_video(youtube, video_path, body):
    from googleapiclient.http import MediaFileUpload

    media = MediaFileUpload(video_path, mimetype="video/mp4", chunksize=8 * 1024 * 1024, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"   ⬆️  {int(status.progress() * 100)}%")
    return response["id"]


def proyectos_pendientes():
    """Proyectos con video final renderizado y sin marca de subida."""
    if not os.path.exists(BASE_DIR):
        return []
    pendientes = []
    for p in sorted(os.listdir(BASE_DIR)):
        path_p = os.path.join(BASE_DIR, p)
        if not os.path.isdir(path_p):
            continue
        video = os.path.join(OUTPUT_DIR, f"{p}_Final.mp4")
        if os.path.exists(video) and not os.path.exists(os.path.join(path_p, MARCA_SUBIDO)):
            pendientes.append((p, path_p, video))
    return pendientes


def fase_subir(privacidad="private", proyecto=None, simular=False):
    if privacidad not in PRIVACIDADES:
        print(f"❌ Privacidad inválida '{privacidad}'. Usa: {', '.join(PRIVACIDADES)}")
        return

    pendientes = proyectos_pendientes()
    if proyecto:
        pendientes = [x for x in pendientes if x[0] == proyecto]

    if not pendientes:
        print("📭 No hay videos pendientes de subir (o ya tienen youtube_subido.json).")
        return

    youtube = None
    if not simular:
        try:
            youtube = obtener_servicio_youtube()
        except Exception as e:
            print(f"❌ No se pudo conectar con YouTube: {e}")
            return

    for nombre, path_p, video in pendientes:
        titulo, hashtags = leer_info_publicacion(path_p)
        body = construir_metadatos(titulo, hashtags)
        body["status"]["privacyStatus"] = privacidad

        print(f"\n📺 {nombre}")
        print(f"   Título: {body['snippet']['title']}")
        print(f"   Hashtags: {' '.join('#' + t for t in body['snippet']['tags'])}")
        print(f"   Privacidad: {privacidad}")

        if simular:
            print("   (simulación: no se sube nada)")
            continue

        try:
            video_id = subir_video(youtube, video, body)
        except Exception as e:
            print(f"   ❌ Error subiendo {nombre}: {e}")
            continue

        url = f"https://youtu.be/{video_id}"
        with open(os.path.join(path_p, MARCA_SUBIDO), "w", encoding="utf-8") as f:
            json.dump({
                "video_id": video_id,
                "url": url,
                "titulo": body["snippet"]["title"],
                "privacidad": privacidad,
                "fecha": datetime.now().isoformat(timespec="seconds"),
            }, f, indent=4, ensure_ascii=False)
        print(f"   ✅ Subido: {url}")
