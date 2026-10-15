"""
VIGILANTE DE GOOGLE DRIVE (100% gratis, sin APIs pagas)

Flujo:
  1. Creas en tu Drive una carpeta por video dentro de la carpeta raíz
     (DRIVE_DIR en el .env, por ejemplo  G:\\Mi unidad\\DataViral).
  2. Dentro pones el guion (guion.txt hecho con Gemini, o el guion.json de PREPARAR)
     y las imágenes aprobadas numeradas: 1.png, 2.png ... (o img_1.png, escena_1.jpg).
  3. Google Drive para escritorio sincroniza la carpeta a tu PC.
  4. Este script detecta cuando la carpeta está completa (una imagen por escena
     y nada cambiando hace un rato), genera la voz gratis con edge-tts, monta el
     video y deja el MP4 dentro de la misma carpeta de Drive con VIDEO_LISTO.txt.

Uso:
  python -m core.tools.drive_watcher              -> vigila cada 60 s
  python -m core.tools.drive_watcher --una-vez    -> revisa una vez y termina
  python -m core.tools.drive_watcher --nuevo "Tema del video" [--canal misterio]
                                                  -> crea la carpeta con la plantilla
"""
import argparse
import json
import os
import random
import re
import shutil
import sys
import time
import traceback

RAIZ_REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if RAIZ_REPO not in sys.path:
    sys.path.insert(0, RAIZ_REPO)

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(RAIZ_REPO, ".env"))
except ImportError:
    pass

# Mismo ffmpeg que usa main.py en Windows
if os.path.exists(r"C:\ffmpeg\bin\ffmpeg.exe"):
    os.environ.setdefault("IMAGEIO_FFMPEG_EXE", r"C:\ffmpeg\bin\ffmpeg.exe")

EXT_IMAGEN = (".png", ".jpg", ".jpeg", ".webp")
MARCA_LISTO = "VIDEO_LISTO.txt"
MARCA_ERROR = "ERROR.txt"
TRABAJO_LOCAL = os.path.join(RAIZ_REPO, "proyectos", "_drive")
MUSIC_DIR = os.path.join(RAIZ_REPO, "assets", "music")
SEGUNDOS_ESTABLE = int(os.getenv("DRIVE_SEGUNDOS_ESTABLE", "60"))
CANAL_POR_DEFECTO = os.getenv("DRIVE_CANAL_POR_DEFECTO", "misterio")

PLANTILLA_GUION = """# canal: {canal}
# titulo: {tema}
# hashtags: #datoscuriosos #viral
#
# Escribe aquí la narración, UN PÁRRAFO POR ESCENA (deja una línea en blanco entre escenas).
# Cada escena necesita su imagen: 1.png para el primer párrafo, 2.png para el segundo, etc.
# Las líneas que empiezan con # o con "Prompt:" se ignoran (puedes dejar ahí el prompt de Gemini).
# Cuando subas todas las imágenes, el video se genera solo.

Escena 1: el gancho.

Escena 2: el contexto.

Escena 3: el desarrollo.

Escena 4: el giro.

Escena 5: el cierre que vuelve al inicio.
"""


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def numero_en_nombre(nombre):
    """1.png, img_01.jpg, escena-3.png -> 1, 1, 3. Sin número -> None."""
    m = re.search(r"(\d+)", os.path.splitext(nombre)[0])
    return int(m.group(1)) if m else None


def listar_imagenes(carpeta):
    """Imágenes numeradas ordenadas por su número (ignora miniaturas y temporales)."""
    imagenes = []
    for f in os.listdir(carpeta):
        if f.startswith((".", "~")) or not f.lower().endswith(EXT_IMAGEN):
            continue
        n = numero_en_nombre(f)
        if n is not None:
            imagenes.append((n, os.path.join(carpeta, f)))
    imagenes.sort()
    return [ruta for _, ruta in imagenes]


def leer_guion_txt(ruta):
    """Convierte un guion.txt (párrafos) al mismo formato que guion.json."""
    with open(ruta, "r", encoding="utf-8-sig") as f:
        lineas = f.read().splitlines()

    meta = {}
    parrafos, actual = [], []
    for linea in lineas:
        limpia = linea.strip()
        if limpia.startswith("#"):
            m = re.match(r"#\s*(canal|titulo|título|hashtags)\s*:\s*(.+)", limpia, re.I)
            if m:
                clave = m.group(1).lower().replace("í", "i")
                meta[clave] = m.group(2).strip()
            continue
        if re.match(r"(prompt|prompt imagen|imagen)\s*:", limpia, re.I):
            continue
        if not limpia:
            if actual:
                parrafos.append(" ".join(actual))
                actual = []
            continue
        actual.append(limpia)
    if actual:
        parrafos.append(" ".join(actual))

    # Quita prefijos tipo "Escena 1:" / "1." que Gemini suele poner
    escenas = []
    for p in parrafos:
        texto = re.sub(r"^(escena\s*\d+\s*[:.\-]|\d+\s*[.):\-])\s*", "", p, flags=re.I).strip()
        if texto:
            escenas.append(texto)

    hashtags = meta.get("hashtags", "").split()
    return {
        "guion": [{"escena": i + 1, "texto": t} for i, t in enumerate(escenas)],
        "titulo_redes": meta.get("titulo", ""),
        "hashtags": hashtags,
        "canal_meta": meta.get("canal", CANAL_POR_DEFECTO).lower(),
    }


def cargar_guion(carpeta):
    ruta_json = os.path.join(carpeta, "guion.json")
    ruta_txt = os.path.join(carpeta, "guion.txt")
    if os.path.exists(ruta_json):
        with open(ruta_json, "r", encoding="utf-8-sig") as f:
            datos = json.load(f)
        datos.setdefault("canal_meta", CANAL_POR_DEFECTO)
        return datos
    if os.path.exists(ruta_txt):
        return leer_guion_txt(ruta_txt)
    return None


def segundos_desde_ultimo_cambio(carpeta):
    ultimo = max((os.path.getmtime(os.path.join(carpeta, f)) for f in os.listdir(carpeta)), default=0)
    return time.time() - ultimo


def estado_carpeta(carpeta):
    """Devuelve (listo: bool, motivo: str, datos, imagenes)."""
    if os.path.exists(os.path.join(carpeta, MARCA_LISTO)):
        return False, "ya montado", None, None
    if os.path.exists(os.path.join(carpeta, MARCA_ERROR)):
        return False, f"tiene {MARCA_ERROR} (bórralo para reintentar)", None, None
    datos = cargar_guion(carpeta)
    if not datos or not datos.get("guion"):
        return False, "falta guion.txt o guion.json", None, None
    imagenes = listar_imagenes(carpeta)
    escenas = len(datos["guion"])
    if len(imagenes) < escenas:
        return False, f"{len(imagenes)}/{escenas} imágenes", datos, imagenes
    espera = SEGUNDOS_ESTABLE - segundos_desde_ultimo_cambio(carpeta)
    if espera > 0:
        return False, f"completa, esperando {int(espera)} s a que termine de sincronizar", datos, imagenes
    return True, "lista", datos, imagenes[:escenas]


def elegir_musica(canal):
    carpeta = os.path.join(MUSIC_DIR, (canal or "").lower().strip())
    if os.path.isdir(carpeta):
        pistas = [f for f in os.listdir(carpeta) if f.lower().endswith((".mp3", ".m4a"))]
        if pistas:
            return os.path.join(carpeta, random.choice(pistas))
    return None


def texto_para_voz(datos):
    from core.config.limpieza_engine import limpiar_texto_para_tts, insertar_pausas_inteligentes
    escenas = datos["guion"]
    return " ".join(
        insertar_pausas_inteligentes(limpiar_texto_para_tts(e["texto"]), i == len(escenas) - 1)
        for i, e in enumerate(escenas)
    ).strip()


def montar_carpeta(carpeta, datos, imagenes):
    """Copia a local, genera voz gratis, renderiza y sube el MP4 a la carpeta de Drive."""
    from core.engines.voice_engine import generar_voz
    from core.editors.video_editor import crear_video_pro_con_imagenes

    nombre = re.sub(r'[\\/*?:"<>|\s]+', "_", os.path.basename(carpeta.rstrip("\\/"))).strip("_")
    local = os.path.join(TRABAJO_LOCAL, nombre)
    if os.path.exists(local):
        shutil.rmtree(local)
    os.makedirs(os.path.join(local, "images"))

    # Copias locales renombradas img_1, img_2... (el editor ordena por ese patrón)
    locales = []
    for i, img in enumerate(imagenes, start=1):
        destino = os.path.join(local, "images", f"img_{i}{os.path.splitext(img)[1].lower()}")
        shutil.copy2(img, destino)
        locales.append(destino)

    audio = os.path.join(local, "audio.mp3")
    timestamps = os.path.join(local, "timestamps.json")
    audio_drive = os.path.join(carpeta, "audio.mp3")
    ts_drive = os.path.join(carpeta, "timestamps.json")
    if os.path.exists(audio_drive) and os.path.exists(ts_drive):
        log("   Usando el audio que ya está en la carpeta.")
        shutil.copy2(audio_drive, audio)
        shutil.copy2(ts_drive, timestamps)
    else:
        log("   Generando voz con edge-tts (gratis)...")
        if not generar_voz(texto_para_voz(datos), audio, timestamps):
            raise RuntimeError("No se pudo generar la voz")

    with open(os.path.join(local, "guion.json"), "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)

    salida_local = os.path.join(RAIZ_REPO, "output", "videos", f"{nombre}_Final.mp4")
    os.makedirs(os.path.dirname(salida_local), exist_ok=True)
    ok = crear_video_pro_con_imagenes(
        datos, audio, timestamps, locales, salida_local,
        musica_path=elegir_musica(datos.get("canal_meta")),
    )
    if not ok or not os.path.exists(salida_local):
        raise RuntimeError("El render no produjo el video")

    shutil.copy2(salida_local, os.path.join(carpeta, os.path.basename(salida_local)))

    titulo = datos.get("titulo_redes") or os.path.basename(carpeta)
    tags = " ".join(datos.get("hashtags") or [])
    with open(os.path.join(carpeta, "info_publicacion.txt"), "w", encoding="utf-8") as f:
        f.write(f"TITULO PARA REDES:\n{titulo}\n\nHASHTAGS:\n{tags}\n")
    with open(os.path.join(carpeta, MARCA_LISTO), "w", encoding="utf-8") as f:
        f.write(f"Video generado el {time.strftime('%Y-%m-%d %H:%M')}: {os.path.basename(salida_local)}\n"
                f"Borra este archivo si quieres volver a generarlo.\n")
    return salida_local


def revisar(raiz):
    carpetas = sorted(
        os.path.join(raiz, d) for d in os.listdir(raiz)
        if os.path.isdir(os.path.join(raiz, d)) and not d.startswith((".", "_"))
    )
    for carpeta in carpetas:
        listo, motivo, datos, imagenes = estado_carpeta(carpeta)
        nombre = os.path.basename(carpeta)
        if not listo:
            if motivo != "ya montado":
                log(f"⏳ {nombre}: {motivo}")
            continue
        log(f"🎬 {nombre}: completa, montando video...")
        try:
            salida = montar_carpeta(carpeta, datos, imagenes)
            log(f"✅ {nombre}: video listo y subido a Drive ({os.path.basename(salida)})")
        except Exception as e:
            log(f"❌ {nombre}: {e}")
            with open(os.path.join(carpeta, MARCA_ERROR), "w", encoding="utf-8") as f:
                f.write(f"{e}\n\n{traceback.format_exc()}\nBorra este archivo para reintentar.\n")


def crear_carpeta_nueva(raiz, tema, canal):
    nombre = re.sub(r'[\\/*?:"<>|]', "", tema).strip()
    carpeta = os.path.join(raiz, nombre)
    os.makedirs(carpeta, exist_ok=True)
    ruta = os.path.join(carpeta, "guion.txt")
    if os.path.exists(ruta):
        log(f"Ya existe {ruta}, no lo sobrescribo.")
    else:
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(PLANTILLA_GUION.format(canal=canal, tema=tema))
        log(f"📁 Carpeta creada: {carpeta}")


def main():
    parser = argparse.ArgumentParser(description="Genera videos desde carpetas de Google Drive")
    parser.add_argument("--carpeta", default=os.getenv("DRIVE_DIR"),
                        help="Carpeta raíz en Drive (por defecto DRIVE_DIR del .env)")
    parser.add_argument("--una-vez", action="store_true", help="Revisa una vez y termina")
    parser.add_argument("--intervalo", type=int, default=60, help="Segundos entre revisiones")
    parser.add_argument("--nuevo", metavar="TEMA", help="Crea una carpeta nueva con la plantilla")
    parser.add_argument("--canal", default=CANAL_POR_DEFECTO, help="Canal para --nuevo")
    args = parser.parse_args()

    if not args.carpeta:
        print("❌ Configura DRIVE_DIR en el .env (ej: DRIVE_DIR=G:\\Mi unidad\\DataViral) o usa --carpeta")
        sys.exit(1)
    os.makedirs(args.carpeta, exist_ok=True)

    if args.nuevo:
        crear_carpeta_nueva(args.carpeta, args.nuevo, args.canal)
        return

    log(f"👀 Vigilando {args.carpeta}")
    while True:
        try:
            revisar(args.carpeta)
        except Exception as e:
            log(f"⚠️ Error revisando la carpeta: {e}")
        if args.una_vez:
            break
        time.sleep(args.intervalo)


if __name__ == "__main__":
    main()
