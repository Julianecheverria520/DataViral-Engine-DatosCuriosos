from moviepy.editor import (
    ImageClip,
    AudioFileClip,
    CompositeVideoClip,
    VideoClip
)
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import json

# ==============================
# CONFIGURACIÓN
# ==============================

WIDTH = 1080
HEIGHT = 1920
FONT_PATH = "C:/Windows/Fonts/arialbd.ttf"
FONT_SIZE = 120
COLOR_TEXTO = (255, 255, 255)

# ==============================
# UTILIDADES
# ==============================

def cargar_fuente(size):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except:
        return ImageFont.load_default()


# ==============================
# SUBTÍTULOS PALABRA POR PALABRA
# ==============================

def crear_subtitulos_palabra(timestamps):

    font = cargar_fuente(FONT_SIZE)
    clips = []

    for p in timestamps:

        palabra = p["palabra"].strip()
        inicio = p["inicio"]
        fin = p["fin"]

        duracion = fin - inicio

        if duracion <= 0.02:
            continue

        # Crear imagen transparente
        img = Image.new("RGBA", (WIDTH, 400), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        bbox = draw.textbbox((0, 0), palabra, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]

        x = (WIDTH - w) // 2
        y = (400 - h) // 2

        # Sombra para legibilidad
        draw.text((x+4, y+4), palabra, font=font, fill=(0, 0, 0, 180))
        draw.text((x, y), palabra, font=font, fill=COLOR_TEXTO)

        np_img = np.array(img)

        clip = (
            ImageClip(np_img)
            .set_start(inicio)
            .set_duration(duracion)
            .set_position(("center", HEIGHT * 0.75))
        )

        clips.append(clip)

    return clips


# ==============================
# BARRA DE PROGRESO
# ==============================

def crear_barra_progreso(duracion_total):

    def frame(t):
        progreso = min(t / duracion_total, 1)
        ancho = int(WIDTH * progreso)
        img = np.zeros((12, WIDTH, 3), dtype=np.uint8)
        img[:, :ancho] = [0, 240, 255]
        return img

    return VideoClip(frame, duration=duracion_total).set_position((0, HEIGHT - 20))


# ==============================
# RENDER FINAL
# ==============================

def crear_video_pro_con_imagenes(
    datos_guion,
    audio_path,
    timestamps_path,
    lista_imagenes,
    output_path
):

    audio = AudioFileClip(audio_path)
    dur_total = audio.duration

    with open(timestamps_path, "r", encoding="utf-8") as f:
        timestamps = json.load(f)

    elementos = []

    # ==============================
    # FONDOS
    # ==============================

    num_escenas = len(datos_guion)
    dur_escena = dur_total / max(num_escenas, 1)

    for i, img_path in enumerate(lista_imagenes):
        if i >= num_escenas:
            break

        clip_img = (
            ImageClip(img_path)
            .set_start(i * dur_escena)
            .set_duration(dur_escena)
            .resize(height=HEIGHT)
            .set_position("center")
        )

        elementos.append(clip_img)

    # ==============================
    # SUBTÍTULOS EXACTOS
    # ==============================

    subs = crear_subtitulos_palabra(timestamps)
    elementos.extend(subs)

    # ==============================
    # BARRA
    # ==============================

    elementos.append(crear_barra_progreso(dur_total))

    # ==============================
    # MONTAJE FINAL
    # ==============================

    final = CompositeVideoClip(elementos, size=(WIDTH, HEIGHT))
    final = final.set_duration(dur_total).set_audio(audio)

    print("🎬 Renderizando video con palabra exacta sincronizada...")

    final.write_videofile(
        output_path,
        fps=30,
        codec="libx264",
        audio_codec="aac",
        audio_fps=44100,   # 🔥 CLAVE para evitar drift
        threads=6,
        preset="fast",
    )

    audio.close()
    final.close()