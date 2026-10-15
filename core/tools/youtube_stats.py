"""
youtube_stats.py - Métricas reales del canal de YouTube usando la YouTube Data API v3
Funciones:
- obtener_estadisticas_canal: suscriptores, vistas totales y número de videos
- obtener_videos_recientes: vistas, likes y comentarios de los últimos videos
- rastrear_estadisticas: ejecuta todo y lo guarda en database/metricas.db y en output/

Requiere en .env:
    YOUTUBE_API_KEY=tu_clave        (Google Cloud > APIs > YouTube Data API v3 > Credenciales)
    YOUTUBE_CHANNEL=@datoscuriososmundo520   (opcional: handle o ID "UC...")
"""

import os
import csv
import json
import sqlite3
import logging
from datetime import datetime

import requests
from dotenv import load_dotenv

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(RAIZ, ".env"))
load_dotenv()

# Nombres aceptados para la clave en el .env (el primero que exista)
NOMBRES_CLAVE = ["YOUTUBE_API_KEY", "YT_API_KEY", "YOUTUBE_KEY", "API_KEY_YOUTUBE", "YOUTUBE_DATA_API_KEY", "GOOGLE_API_KEY"]

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

API_URL = "https://www.googleapis.com/youtube/v3"
CANAL_POR_DEFECTO = "@datoscuriososmundo520"
DB_PATH = os.path.join("database", "metricas.db")
CSV_CANAL = os.path.join("output", "metricas_youtube_canal.csv")
CSV_VIDEOS = os.path.join("output", "metricas_youtube_videos.csv")


class YouTubeAPIError(Exception):
    pass


def _llamar_api(recurso, api_key, **params):
    params["key"] = api_key
    resp = requests.get(f"{API_URL}/{recurso}", params=params, timeout=30)
    if resp.status_code != 200:
        try:
            mensaje = resp.json()["error"]["message"]
        except Exception:
            mensaje = resp.text[:300]
        raise YouTubeAPIError(f"{recurso} ({resp.status_code}): {mensaje}")
    return resp.json()


# ============================================================
# FUNCIÓN 1: Canal
# ============================================================

def obtener_estadisticas_canal(api_key, canal=CANAL_POR_DEFECTO):
    """Acepta un handle (@nombre) o un ID de canal (UC...)."""
    if canal.startswith("UC"):
        filtro = {"id": canal}
    else:
        filtro = {"forHandle": canal if canal.startswith("@") else f"@{canal}"}

    data = _llamar_api("channels", api_key, part="snippet,statistics,contentDetails", **filtro)
    items = data.get("items", [])
    if not items:
        raise YouTubeAPIError(f"No se encontró el canal '{canal}'")

    item = items[0]
    stats = item["statistics"]
    return {
        "id": item["id"],
        "titulo": item["snippet"]["title"],
        "url": f"https://www.youtube.com/channel/{item['id']}",
        "suscriptores": int(stats.get("subscriberCount", 0)),
        "vistas_totales": int(stats.get("viewCount", 0)),
        "videos": int(stats.get("videoCount", 0)),
        "playlist_subidas": item["contentDetails"]["relatedPlaylists"]["uploads"],
    }


# ============================================================
# FUNCIÓN 2: Videos recientes
# ============================================================

def obtener_videos_recientes(api_key, playlist_subidas, max_videos=50):
    ids = []
    page_token = None
    while len(ids) < max_videos:
        params = {"part": "contentDetails", "playlistId": playlist_subidas,
                  "maxResults": min(50, max_videos - len(ids))}
        if page_token:
            params["pageToken"] = page_token
        data = _llamar_api("playlistItems", api_key, **params)
        ids += [i["contentDetails"]["videoId"] for i in data.get("items", [])]
        page_token = data.get("nextPageToken")
        if not page_token:
            break

    videos = []
    for inicio in range(0, len(ids), 50):
        data = _llamar_api("videos", api_key, part="snippet,statistics", id=",".join(ids[inicio:inicio + 50]))
        for item in data.get("items", []):
            stats = item.get("statistics", {})
            videos.append({
                "id": item["id"],
                "titulo": item["snippet"]["title"],
                "publicado": item["snippet"]["publishedAt"],
                "url": f"https://www.youtube.com/shorts/{item['id']}",
                "vistas": int(stats.get("viewCount", 0)),
                "likes": int(stats.get("likeCount", 0)),
                "comentarios": int(stats.get("commentCount", 0)),
            })
    return videos


# ============================================================
# GUARDADO
# ============================================================

def _guardar_db(fecha, canal, videos):
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS metricas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT,
                tipo TEXT,  -- 'perfil' o 'video'
                url TEXT,
                seguidores INTEGER,
                likes_totales INTEGER,
                vistas_totales INTEGER,
                comentarios INTEGER,
                shares INTEGER,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""")
        conn.execute(
            "INSERT INTO metricas (fecha, tipo, url, seguidores, likes_totales, vistas_totales, comentarios, shares, metadata) "
            "VALUES (?, 'perfil', ?, ?, 0, ?, 0, 0, ?)",
            (fecha, canal["url"], canal["suscriptores"], canal["vistas_totales"],
             json.dumps({"plataforma": "youtube", "titulo": canal["titulo"], "videos": canal["videos"]}, ensure_ascii=False)))
        conn.executemany(
            "INSERT INTO metricas (fecha, tipo, url, seguidores, likes_totales, vistas_totales, comentarios, shares, metadata) "
            "VALUES (?, 'video', ?, 0, ?, ?, ?, 0, ?)",
            [(fecha, v["url"], v["likes"], v["vistas"], v["comentarios"],
              json.dumps({"plataforma": "youtube", "titulo": v["titulo"], "publicado": v["publicado"]}, ensure_ascii=False))
             for v in videos])
        conn.commit()
    finally:
        conn.close()


def _guardar_csv(fecha, canal, videos):
    os.makedirs("output", exist_ok=True)

    nuevo = not os.path.exists(CSV_CANAL)
    with open(CSV_CANAL, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if nuevo:
            w.writerow(["fecha", "canal", "suscriptores", "vistas_totales", "videos"])
        w.writerow([fecha, canal["titulo"], canal["suscriptores"], canal["vistas_totales"], canal["videos"]])

    nuevo = not os.path.exists(CSV_VIDEOS)
    with open(CSV_VIDEOS, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if nuevo:
            w.writerow(["fecha", "titulo", "publicado", "vistas", "likes", "comentarios", "url"])
        for v in videos:
            w.writerow([fecha, v["titulo"], v["publicado"], v["vistas"], v["likes"], v["comentarios"], v["url"]])


# ============================================================
# EJECUCIÓN COMPLETA
# ============================================================

def rastrear_estadisticas(canal=None, max_videos=50):
    api_key = next((os.getenv(n) for n in NOMBRES_CLAVE if os.getenv(n)), None)
    canal = canal or os.getenv("YOUTUBE_CHANNEL") or CANAL_POR_DEFECTO
    if not api_key:
        print(f"❌ No encontré la clave de YouTube en {os.path.join(RAIZ, '.env')}")
        print(f"   Nombres que busco: {', '.join(NOMBRES_CLAVE)}")
        print("   Créala en https://console.cloud.google.com/apis/credentials (habilita 'YouTube Data API v3').")
        return None

    try:
        datos_canal = obtener_estadisticas_canal(api_key, canal)
        videos = obtener_videos_recientes(api_key, datos_canal["playlist_subidas"], max_videos)
    except (YouTubeAPIError, requests.RequestException) as e:
        logger.error(f"Error consultando la API de YouTube: {e}")
        return None

    fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
    _guardar_db(fecha, datos_canal, videos)
    _guardar_csv(fecha, datos_canal, videos)

    print(f"\n📺 {datos_canal['titulo']}  ({fecha})")
    print(f"   👥 Suscriptores: {datos_canal['suscriptores']:,}")
    print(f"   👀 Vistas totales: {datos_canal['vistas_totales']:,}")
    print(f"   🎬 Videos: {datos_canal['videos']:,}")
    if videos:
        print(f"\n🏆 Top videos (de los últimos {len(videos)}):")
        for v in sorted(videos, key=lambda x: x["vistas"], reverse=True)[:10]:
            print(f"   {v['vistas']:>9,} vistas | {v['likes']:>6,} likes | {v['titulo'][:60]}")
    print(f"\n💾 Guardado en {DB_PATH}, {CSV_CANAL} y {CSV_VIDEOS}")

    return {"canal": datos_canal, "videos": videos}


if __name__ == "__main__":
    rastrear_estadisticas()
