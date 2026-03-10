from moviepy.editor import ImageClip, VideoClip
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
import json
import re

# ==============================
# CONFIGURACIÓN ESTÁTICA
# ==============================
WIDTH = 1080
HEIGHT = 1920
FONT_PATH = "C:/Windows/Fonts/arialbd.ttf"

COLOR_BASE = (255, 255, 255)       
COLOR_KARAOKE = (255, 255, 0)      
COLOR_STROKE = (0, 0, 0)           

def cargar_fuente(size):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except:
        return ImageFont.load_default()

# ==============================
# DIBUJO DE PALABRA (LIENZO SEGURO Y ESCALA PIL)
# ==============================
def crear_clip_palabra(texto, size, color, es_activa=False):
    # Si es activa, dibujamos la fuente un 10% más grande en lugar de usar resize de MoviePy
    current_size = int(size * 1.1) if es_activa else size
    font = cargar_fuente(current_size)
    
    test_draw = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    bbox = test_draw.textbbox((0, 0), texto, font=font)
    
    # Padding generoso para evitar CUALQUIER corte (15% del ancho de la palabra)
    w_txt = bbox[2] - bbox[0]
    h_txt = bbox[3] - bbox[1]
    pad_w = int(w_txt * 0.20) + 40 
    pad_h = 50
    
    img = Image.new("RGBA", (int(w_txt + pad_w*2), int(h_txt + pad_h*2)), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    pos = (pad_w, pad_h)
    
    # Borde negro (Stroke)
    draw.text(pos, texto, font=font, fill=COLOR_STROKE, stroke_width=12, stroke_fill=COLOR_STROKE)

    if es_activa:
        # Glow sutil (Opacidad reducida para no deformar la letra)
        glow_img = Image.new("RGBA", img.size, (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow_img)
        glow_draw.text(pos, texto, font=font, fill=color + (150,), stroke_width=6)
        glow_img = glow_img.filter(ImageFilter.GaussianBlur(radius=7))
        img.paste(glow_img, (0, 0), glow_img)

    draw.text(pos, texto, font=font, fill=color)
    
    # Retornamos el clip y el padding usado para posicionamiento exacto
    return ImageClip(np.array(img)), pad_w, pad_h

# ==============================
# SUBTÍTULOS POR BLOQUE (CON AUTO-ESCALADO)
# ==============================
def crear_subtitulos_bloque(timestamps_path, palabras_por_bloque=4):
    try:
        with open(timestamps_path, "r", encoding="utf-8") as f:
            timestamps = json.load(f)
    except: return []

    clips = []
    bloques = [timestamps[i:i + palabras_por_bloque] for i in range(0, len(timestamps), palabras_por_bloque)]

    for bloque in bloques:
        t_inicio_bloque = bloque[0]["inicio"]
        
        # --- LÓGICA DE AUTO-AJUSTE DE TAMAÑO ---
        base_size = 95
        font_test = cargar_fuente(base_size)
        draw_test = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
        
        frase_completa = " ".join([p["palabra"].upper() for p in bloque])
        # Si la frase en una línea es muy larga, bajamos el tamaño base
        w_total_test = draw_test.textbbox((0, 0), frase_completa, font=font_test)[2]
        
        if w_total_test > WIDTH * 0.85:
            base_size = 75 # Reducimos fuente para que quepa en pantalla
            font_test = cargar_fuente(base_size)

        lineas = [bloque[:2], bloque[2:]] if len(bloque) > 2 else [bloque]
        y_base = HEIGHT * 0.72

        for l_idx, linea in enumerate(lineas):
            textos_linea = [p["palabra"].upper() for p in linea]
            frase_txt = " ".join(textos_linea)
            
            w_frase = draw_test.textbbox((0, 0), frase_txt, font=font_test)[2]
            w_espacio = draw_test.textbbox((0, 0), " ", font=font_test)[2] + 30 # Espacio extra entre palabras
            
            x_cursor = (WIDTH - w_frase - (len(linea)-1)*30) // 2
            y_actual = y_base + (l_idx * (base_size + 40))

            for p_data in linea:
                palabra = p_data["palabra"].upper()
                w_p = draw_test.textbbox((0, 0), palabra, font=font_test)[2]
                
                # 1. PALABRA BLANCA
                dur_blanca = p_data["inicio"] - t_inicio_bloque
                if dur_blanca > 0.05:
                    c_blanca, pad_w, pad_h = crear_clip_palabra(palabra, base_size, COLOR_BASE)
                    clips.append(c_blanca.set_start(t_inicio_bloque)
                                       .set_duration(dur_blanca)
                                       .set_position((x_cursor - pad_w, y_actual - pad_h)))

                # 2. PALABRA AMARILLA (Dibujada más grande nativamente)
                c_amarilla, pad_w_a, pad_h_a = crear_clip_palabra(palabra, base_size, COLOR_KARAOKE, es_activa=True)
                
                # Ajuste de posición para que el "crecimiento" sea céntrico
                offset_x = (pad_w_a - (int(w_p * 0.20) + 20)) # Diferencia de paddings
                
                clips.append(c_amarilla.set_start(p_data["inicio"])
                                         .set_duration(max(0.1, p_data["fin"] - p_data["inicio"]))
                                         .set_position((x_cursor - pad_w_a, y_actual - pad_h_a)))

                x_cursor += w_p + w_espacio

    return clips

# ==============================
# BARRA DE PROGRESO (SIN CAMBIOS)
# ==============================
def crear_barra_progreso(duracion_total):
    bar_w, bar_h = WIDTH - 350, 16
    x0, y0 = (WIDTH - bar_w) // 2, 50
    def frame(t):
        img = Image.new("RGB", (WIDTH, 120), (0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.rectangle([x0, y0, x0 + bar_w, y0 + bar_h], fill=(40, 40, 40))
        progreso = min(t / duracion_total, 1.0)
        if progreso > 0:
            draw.rectangle([x0, y0, x0 + int(bar_w * progreso), y0 + bar_h], fill=(0, 240, 255))
        return np.array(img)
    return VideoClip(frame, duration=duracion_total).set_position((0, HEIGHT - 140))