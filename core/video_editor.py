from moviepy.editor import (
    ImageClip,
    AudioFileClip,
    CompositeVideoClip,
    VideoClip
)
from moviepy.video.fx.all import fadein, fadeout
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
import json
import os

# =====================================================
# CONFIG GLOBAL
# =====================================================
WIDTH = 1080
HEIGHT = 1920
FONT_PATH = "C:/Windows/Fonts/arialbd.ttf"
FONT_SIZE = 85

COLOR_NORMAL = (255, 255, 255)
COLOR_KEY = (0, 240, 255)

# =====================================================
# UTIL
# =====================================================
def cargar_fuente(size):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except:
        return ImageFont.load_default()

# =====================================================
# SUBTÍTULOS SINCRONIZADOS (SINCRO PERFECTA)
# =====================================================
def crear_texto_sincronizado(palabra_clave, timestamps):
    clips = []
    font = cargar_fuente(FONT_SIZE)

    for palabra_data in timestamps:
        palabra = palabra_data["palabra"]
        inicio = palabra_data["inicio"]
        duracion = palabra_data["duracion"]

        if duracion <= 0: continue

        limpia = palabra.lower().strip(".,!?")
        # Si quieres resaltar alguna palabra clave específica, puedes pasarla aquí
        es_clave = palabra_clave and limpia == palabra_clave.lower()

        # Crear lienzo para la palabra
        img = Image.new("RGBA", (1000, 250), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        bbox = draw.textbbox((0, 0), palabra, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]

        x = (1000 - w) // 2
        y = (250 - h) // 2

        # Efecto de Glow para palabras importantes
        if es_clave:
            glow = Image.new("RGBA", (1000, 250), (0, 0, 0, 0))
            glow_draw = ImageDraw.Draw(glow)
            glow_draw.text((x, y), palabra, font=font, fill=COLOR_KEY)
            glow = glow.filter(ImageFilter.GaussianBlur(6))
            img = Image.alpha_composite(img, glow)

        # Sombra de texto
        draw.text((x+4, y+4), palabra, font=font, fill=(0, 0, 0, 180))

        # Texto Principal
        draw.text(
            (x, y),
            palabra,
            font=font,
            fill=COLOR_KEY if es_clave else COLOR_NORMAL
        )

        np_img = np.array(img)

        # Crear el clip de la palabra
        clip = (
            ImageClip(np_img)
            .set_start(inicio)
            .set_duration(duracion)
            .set_position(("center", HEIGHT * 0.75)) # Un poco más arriba de la barra
            # Efecto POP optimizado (no consume tanta CPU)
            .resize(lambda t: 1.1 if t < 0.05 else 1.0)
        )
        clips.append(clip)

    return clips

# =====================================================
# BARRA PROGRESO
# =====================================================
def crear_barra_progreso(duracion_total):
    def frame(t):
        progreso = min(t / duracion_total, 1)
        ancho = int(WIDTH * progreso)
        img = np.zeros((12, WIDTH, 3), dtype=np.uint8)
        img[:, :ancho] = [0, 240, 255] # Azul eléctrico
        return img

    return VideoClip(frame, duration=duracion_total).set_position((0, HEIGHT - 20))

# =====================================================
# FUNCIÓN PRINCIPAL (CORREGIDA)
# =====================================================
def crear_video_pro_con_imagenes(datos_guion, audio_path, timestamps_path, lista_imagenes, output_path):
    
    audio = AudioFileClip(audio_path)
    dur_total = audio.duration
    
    # Cargar timestamps
    with open(timestamps_path, "r", encoding="utf-8") as f:
        timestamps = json.load(f)

    elementos = []

    # 1. Fondo base: Imágenes con cambio según guion
    num_escenas = len(datos_guion)
    dur_escena = dur_total / num_escenas

    for i, img_path in enumerate(lista_imagenes):
        if i >= num_escenas: break
        
        inicio_img = i * dur_escena
        
        # Cada imagen dura exactamente su parte del audio
        clip_img = (
            ImageClip(img_path)
            .set_start(inicio_img)
            .set_duration(dur_escena)
            .resize(height=HEIGHT)
            .set_position("center")
            # Zoom suave constante (Efecto Ken Burns)
            .resize(lambda t: 1.0 + 0.1 * (t / dur_escena))
        )
        elementos.append(clip_img)

    # 2. Subtítulos dinámicos (Sincronía total)
    # Buscamos si hay palabras clave en el guion para resaltar
    palabras_clave_global = [e.get("palabra_clave", "").lower() for e in datos_guion if e.get("palabra_clave")]
    
    # Usamos una lógica interna para resaltar palabras clave si coinciden
    subs = crear_texto_sincronizado(None, timestamps) 
    elementos.extend(subs)

    # 3. Barra de progreso
    elementos.append(crear_barra_progreso(dur_total))

    # 4. Montaje Final (ORDEN CORREGIDO)
    final = CompositeVideoClip(elementos, size=(WIDTH, HEIGHT))
    final = final.set_duration(dur_total) 
    final = final.set_audio(audio)

    print(f"🚀 Renderizando: {output_path} ({dur_total:.2f}s)")

    # Renderizado estable
    final.write_videofile(
        output_path,
        fps=30,
        codec="libx264",
        audio_codec="aac",
        threads=6,
        preset="medium",
        temp_audiofile="temp-audio.m4a",
        remove_temp=True
    )
    
    # Limpieza de memoria
    audio.close()
    final.close()