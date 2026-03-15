from moviepy.editor import TextClip, CompositeVideoClip
from PIL import ImageFont
import textwrap

FONT_PATH = "assets/fonts/Montserrat-Bold.ttf"  # Ajusta si usas otra
FONT_SIZE = 90
COLOR_NORMAL = "white"
COLOR_ACTIVA = "yellow"
STROKE_COLOR = "black"
STROKE_WIDTH = 4

MAX_WIDTH_RATIO = 0.85  # 85% del ancho del video


def dividir_en_bloques(timestamps, max_palabras=6):
    bloques = []
    actual = []

    for palabra in timestamps:
        actual.append(palabra)

        if len(actual) >= max_palabras:
            bloques.append(actual)
            actual = []

    if actual:
        bloques.append(actual)

    return bloques


def construir_linea(palabras):
    return " ".join([p["palabra"] for p in palabras])


def crear_subtitulos_karaoke(video, timestamps):

    ancho_video = video.w
    alto_video = video.h
    max_width = int(ancho_video * MAX_WIDTH_RATIO)

    bloques = dividir_en_bloques(timestamps, max_palabras=5)

    clips = []

    for bloque in bloques:

        inicio_bloque = bloque[0]["inicio"]
        fin_bloque = bloque[-1]["fin"]

        texto_completo = construir_linea(bloque)

        # Clip base blanco
        base = TextClip(
            texto_completo,
            fontsize=FONT_SIZE,
            font=FONT_PATH,
            color=COLOR_NORMAL,
            stroke_color=STROKE_COLOR,
            stroke_width=STROKE_WIDTH,
            size=(max_width, None),
            method="caption",
        ).set_position(("center", alto_video * 0.75)).set_start(inicio_bloque).set_end(fin_bloque)

        clips.append(base)

        # Palabra activa
        for palabra in bloque:

            palabra_clip = TextClip(
                texto_completo,
                fontsize=FONT_SIZE,
                font=FONT_PATH,
                color=COLOR_NORMAL,
                stroke_color=STROKE_COLOR,
                stroke_width=STROKE_WIDTH,
                size=(max_width, None),
                method="caption",
            )

            texto_karaoke = ""

            for p in bloque:
                if p == palabra:
                    texto_karaoke += f"<span foreground='{COLOR_ACTIVA}'>{p['palabra']}</span> "
                else:
                    texto_karaoke += p["palabra"] + " "

            activa = TextClip(
                texto_karaoke.strip(),
                fontsize=FONT_SIZE,
                font=FONT_PATH,
                method="caption",
                size=(max_width, None),
            ).set_position(("center", alto_video * 0.75)) \
             .set_start(palabra["inicio"]) \
             .set_end(palabra["fin"])

            clips.append(activa)

    return CompositeVideoClip([video] + clips)