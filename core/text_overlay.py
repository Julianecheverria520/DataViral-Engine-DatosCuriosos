from PIL import Image, ImageDraw, ImageFont
import numpy as np
from moviepy.editor import ImageClip


def crear_texto_clip(
    texto,
    ancho=1080,
    alto=1920,
    tamaño_fuente=90,
    color_texto="white",
    color_fondo=(0, 0, 0, 180),
    duracion=5
):
    # Crear imagen RGBA transparente
    img = Image.new("RGBA", (ancho, alto), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    try:
        fuente = ImageFont.truetype("arial.ttf", tamaño_fuente)
    except:
        fuente = ImageFont.load_default()

    # Ajustar texto en múltiples líneas
    margen = 100
    max_ancho = ancho - margen * 2

    lineas = []
    palabras = texto.split()
    linea_actual = ""

    for palabra in palabras:
        test_linea = linea_actual + " " + palabra if linea_actual else palabra
        bbox = draw.textbbox((0, 0), test_linea, font=fuente)
        if bbox[2] - bbox[0] <= max_ancho:
            linea_actual = test_linea
        else:
            lineas.append(linea_actual)
            linea_actual = palabra

    if linea_actual:
        lineas.append(linea_actual)

    altura_total = 0
    alturas = []

    for linea in lineas:
        bbox = draw.textbbox((0, 0), linea, font=fuente)
        altura = bbox[3] - bbox[1]
        alturas.append(altura)
        altura_total += altura + 20

    y_texto = (alto - altura_total) // 2

    # Fondo semi-transparente
    fondo = Image.new("RGBA", (ancho, alto), color_fondo)
    img = Image.alpha_composite(img, fondo)

    for i, linea in enumerate(lineas):
        bbox = draw.textbbox((0, 0), linea, font=fuente)
        ancho_texto = bbox[2] - bbox[0]

        x = (ancho - ancho_texto) // 2

        draw.text((x, y_texto), linea, font=fuente, fill=color_texto)
        y_texto += alturas[i] + 20

    np_img = np.array(img)

    clip = ImageClip(np_img).set_duration(duracion)
    return clip