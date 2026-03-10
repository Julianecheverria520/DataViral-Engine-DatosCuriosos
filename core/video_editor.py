import json
import os
import re
import sys
import time
import numpy as np
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip, VideoClip, CompositeAudioClip, afx
from moviepy.config import change_settings

# ==========================================================
# CONFIGURACIÓN DE RUTAS Y BINARIOS
# ==========================================================
# Ajusta esta ruta si tu FFmpeg está en otra ubicación
FFMPEG_PATH = r"C:\ffmpeg\bin\ffmpeg.exe"
if os.path.exists(FFMPEG_PATH):
    change_settings({"FFMPEG_BINARY": FFMPEG_PATH})

try:
    # Importamos los efectos de texto y barra desde tu core
    from core.efectos import crear_subtitulos_bloque, crear_barra_progreso
except ImportError as e:
    print(f"❌ Error crítico: No se pudo importar efectos.py. Detalle: {e}")
    sys.exit(1)

# Parámetros de Redes Sociales (Vertical 9:16)
WIDTH = 1080
HEIGHT = 1920
FPS = 30

# ==========================================================
# UTILIDADES DE SOPORTE
# ==========================================================
def obtener_numero_escena(filename):
    """Extrae el índice de la imagen (img_0, img_1...) para ordenar el montaje."""
    match = re.search(r'img_(\d+)', filename)
    return int(match.group(1)) if match else 999

def limpiar_memoria_clips(clips):
    """Cierra los clips para liberar RAM tras el renderizado."""
    for clip in clips:
        try:
            clip.close()
        except:
            pass

# ==========================================================
# FUNCIÓN PRINCIPAL DE MONTAJE
# ==========================================================
def crear_video_pro_con_imagenes(datos_guion, audio_path, timestamps_path, lista_imagenes, output_path, musica_path=None):
    inicio_proceso = time.time()
    print(f"\n🎬 INICIANDO RENDER PROFESIONAL | InsightdataMind")
    
    if not os.path.exists(audio_path):
        print(f"❌ Error: No se encontró el archivo de voz en {audio_path}")
        return False

    try:
        # 1. CARGA Y PROCESAMIENTO DE AUDIO
        audio_voz = AudioFileClip(audio_path)
        duracion_total = audio_voz.duration

        # Mezcla con música de fondo si se proporciona
        if musica_path and os.path.exists(musica_path):
            print(f"   🎵 Mezclando atmósfera musical: {os.path.basename(musica_path)}")
            audio_fondo = AudioFileClip(musica_path)
            
            # Loop automático si la música es más corta que el video
            if audio_fondo.duration < duracion_total:
                audio_fondo = audio_fondo.fx(afx.audio_loop, duration=duracion_total)
            else:
                audio_fondo = audio_fondo.subclip(0, duracion_total)
            
            # Ajuste de volumen (0.08 - 0.10 es ideal para que la voz resalte)
            audio_fondo = audio_fondo.volumex(0.08).audio_fadeout(2)
            audio_final = CompositeAudioClip([audio_voz, audio_fondo])
        else:
            audio_final = audio_voz

        elementos_video = []

        # 2. PROCESAMIENTO DE IMÁGENES CON ZOOM DINÁMICO
        escenas_guion = datos_guion.get("guion", [])
        num_escenas = len(escenas_guion)
        
        # Ordenamos las imágenes por su nombre (img_0, img_1...)
        lista_imagenes.sort(key=obtener_numero_escena)
        
        # Calculamos la duración exacta por escena para sincronía perfecta
        duracion_escena = duracion_total / len(lista_imagenes) if lista_imagenes else 0

        for i, img_path in enumerate(lista_imagenes):
            if i >= num_escenas and num_escenas > 0: break
            
            start_t = i * duracion_escena
            
            # Creamos el clip de imagen con efecto Zoom (Ken Burns)
            fondo = (
                ImageClip(img_path)
                .set_start(start_t)
                .set_duration(duracion_escena)
                .resize(height=HEIGHT) # Ajuste vertical
                .set_position("center")
                # Zoom suave del 100% al 106% durante la duración de la escena
                .resize(lambda t: 1.0 + 0.06 * (t / duracion_escena))
            )
            elementos_video.append(fondo)

        # 3. CAPA DE SUBTÍTULOS (Sincronizados con el JSON corregido)
        # Usamos 3 palabras por bloque para evitar que se amontonen o descuadren
        print("   ✍️ Generando subtítulos dinámicos...")
        subtitulos_clips = crear_subtitulos_bloque(timestamps_path, palabras_por_bloque=3)
        if subtitulos_clips:
            elementos_video.extend(subtitulos_clips)

        # 4. CAPA DE BARRA DE PROGRESO
        barra = crear_barra_progreso(duracion_total)
        elementos_video.append(barra)

        # 5. COMPOSICIÓN FINAL Y EXPORTACIÓN
        video_final = CompositeVideoClip(elementos_video, size=(WIDTH, HEIGHT))
        video_final = video_final.set_audio(audio_final).set_duration(duracion_total)

        print(f"   🚀 Exportando a: {output_path}")
        video_final.write_videofile(
            output_path,
            fps=FPS,
            codec="libx264",
            audio_codec="aac",
            temp_audiofile="temp-audio.m4a",
            remove_temp=True,
            threads=8,
            preset="medium" # Cambia a "ultrafast" para pruebas rápidas
        )

        # Limpieza de recursos
        audio_final.close()
        video_final.close()
        limpiar_memoria_clips(elementos_video)
        
        print(f"⭐ PROCESO FINALIZADO EXITOSAMENTE EN {time.time() - inicio_proceso:.2f}s")
        return True

    except Exception as e:
        print(f"❌ ERROR CRÍTICO EN VIDEO_EDITOR: {e}")
        return False