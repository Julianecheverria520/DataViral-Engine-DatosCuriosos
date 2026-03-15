from moviepy.editor import ImageClip
from PIL import Image, ImageDraw, ImageFont
import numpy as np

WIDTH = 1080
HEIGHT = 1920
FONT_PATH = "C:/Windows/Fonts/arialbd.ttf"

COLOR_BASE = (255, 255, 255)
COLOR_AMARILLO = (255, 255, 0)
COLOR_ROJO = (255, 60, 60)
COLOR_VERDE = (0, 255, 120)
COLOR_NARANJA = (255, 140, 0)


def cargar_fuente(size):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except:
        return ImageFont.load_default()


def obtener_color_dinamico(palabra, datos_guion):
    palabra_lower = palabra.lower()

    if "mentira" in palabra_lower or "trampa" in palabra_lower:
        return COLOR_ROJO

    if "dinero" in palabra_lower or "ingreso" in palabra_lower:
        return COLOR_VERDE

    if "exige" in palabra_lower or "decide" in palabra_lower or "poder" in palabra_lower:
        return COLOR_NARANJA

    return COLOR_AMARILLO


def crear_subtitulos_karaoke(timestamps, datos_guion, palabras_por_bloque=4):

    font = cargar_fuente(105)
    clips = []
    bloques = []
    bloque_actual = []

    for t in timestamps:
        bloque_actual.append(t)
        if len(bloque_actual) >= palabras_por_bloque:
            bloques.append(bloque_actual)
            bloque_actual = []

    if bloque_actual:
        bloques.append(bloque_actual)

    for bloque in bloques:

        inicio = bloque[0]["inicio"]
        fin = bloque[-1]["fin"]
        duracion = fin - inicio

        if duracion <= 0.02:
            continue

        palabras = [b["palabra"] for b in bloque]

        lineas = []
        actual = ""
        draw_test = ImageDraw.Draw(Image.new("RGBA", (1, 1)))

        for palabra in palabras:
            prueba = actual + palabra + " "
            bbox = draw_test.textbbox((0, 0), prueba, font=font)
            ancho = bbox[2] - bbox[0]

            if ancho <= WIDTH * 0.85:
                actual = prueba
            else:
                lineas.append(actual.strip())
                actual = palabra + " "

        if actual:
            lineas.append(actual.strip())

        lineas = lineas[:2]

        img_base = Image.new("RGBA", (WIDTH, 500), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img_base)

        y_cursor = 0

        for linea in lineas:
            bbox = draw.textbbox((0, 0), linea, font=font)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]

            x = (WIDTH - w) // 2
            draw.text((x+4, y_cursor+4), linea, font=font, fill=(0,0,0,200))
            draw.text((x, y_cursor), linea, font=font, fill=COLOR_BASE)

            y_cursor += h + 20

        base_clip = (
            ImageClip(np.array(img_base))
            .set_start(inicio)
            .set_duration(duracion)
            .set_position(("center", HEIGHT * 0.72))
        )

        clips.append(base_clip)

        palabra_index = 0
        y_cursor = 0

        for linea in lineas:
            palabras_linea = linea.split()
            bbox_linea = draw_test.textbbox((0,0), linea, font=font)
            linea_width = bbox_linea[2] - bbox_linea[0]
            x_cursor = (WIDTH - linea_width) // 2

            for palabra_texto in palabras_linea:

                palabra_data = bloque[palabra_index]

                img_active = Image.new("RGBA", (WIDTH, 500), (0, 0, 0, 0))
                draw_active = ImageDraw.Draw(img_active)

                bbox = draw_active.textbbox((0, 0), palabra_texto, font=font)
                w = bbox[2] - bbox[0]
                h = bbox[3] - bbox[1]

                color = obtener_color_dinamico(palabra_texto, datos_guion)

                draw_active.text((x_cursor+4, y_cursor+4), palabra_texto, font=font, fill=(0,0,0,200))
                draw_active.text((x_cursor, y_cursor), palabra_texto, font=font, fill=color)

                active_clip = (
                    ImageClip(np.array(img_active))
                    .set_start(palabra_data["inicio"])
                    .set_duration(palabra_data["fin"] - palabra_data["inicio"])
                    .set_position(("center", HEIGHT * 0.72))
                )

                clips.append(active_clip)

                x_cursor += w + 30
                palabra_index += 1

            y_cursor += h + 20

    return clips