import json
import os
import re
import sys
import time
import numpy as np
import PIL.Image
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip, VideoClip, CompositeAudioClip, afx, TextClip
from moviepy.config import change_settings

# ==========================================================
# PARCHE DE COMPATIBILIDAD PILLOW
# ==========================================================
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS

# ==========================================================
# CONFIGURACIÓN DE RUTAS
# ==========================================================
FFMPEG_PATH = r"C:\ffmpeg\bin\ffmpeg.exe"
MAGICK_PATH = r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"

if os.path.exists(FFMPEG_PATH):
    change_settings({"FFMPEG_BINARY": FFMPEG_PATH})
if os.path.exists(MAGICK_PATH):
    change_settings({"IMAGEMAGICK_BINARY": MAGICK_PATH})

try:
    from core.efectos import crear_subtitulos_bloque
    print("✅ Módulo de efectos cargado con éxito")
except ImportError:
    print("⚠️ No se encontró efectos.py. Los subtítulos podrían no generarse.")
    crear_subtitulos_bloque = None

WIDTH, HEIGHT, FPS = 1080, 1920, 30

# ==========================================================
# MOTORES DE EFECTOS (SIN MAREO Y SINCRONIZADOS)
# ==========================================================
def aplicar_respiracion_asmr_suave(clip):
    """Movimiento orgánico muy lento (0.12Hz) para evitar mareos."""
    return clip.resize(lambda t: 1.02 + 0.02 * np.sin(2 * np.pi * 0.12 * t))

def crear_barra_progreso_neon_2026(duracion_total):
    """Barra Cian Neón en la base. 3 canales RGB para estabilidad."""
    def make_frame(t):
        progreso = min(t / duracion_total, 1.0)
        ancho_actual = int(WIDTH * progreso)
        barra = np.zeros((12, WIDTH, 3), dtype=np.uint8)
        barra[:, :, :] = 15
        if ancho_actual > 0:
            barra[:, :ancho_actual, 0] = 0
            barra[:, :ancho_actual, 1] = 251
            barra[:, :ancho_actual, 2] = 255
        return barra

    return (VideoClip(make_frame, duration=duracion_total)
            .set_position(("center", HEIGHT - 20))
            .set_opacity(0.9))

# ==========================================================
# FUNCIÓN MAESTRA DE RENDERIZADO
# ==========================================================
def crear_video_pro_con_imagenes(datos_guion, audio_path, timestamps_path, 
                                  lista_imagenes, output_path, musica_path=None, 
                                  viral_mode=True):
    inicio_proceso = time.time()
    output_path = output_path.replace(" ", "_")
    
    print(f"\n🎬 RENDER ENGINE ULTRA 2026 | Sincronía Activa")
    
    if not os.path.exists(audio_path):
        print(f"❌ Error: Audio no encontrado en {audio_path}")
        return False

    try:
        # 1. MEZCLA DE AUDIO
        audio_voz = AudioFileClip(audio_path)
        duracion_total = audio_voz.duration

        if musica_path and os.path.exists(musica_path):
            audio_fondo = AudioFileClip(musica_path).fx(afx.audio_loop, duration=duracion_total)
            audio_fondo = audio_fondo.volumex(0.07).audio_fadeout(2)
            audio_final = CompositeAudioClip([audio_voz, audio_fondo])
        else:
            audio_final = audio_voz

        elementos_video = []

        # 2. CAPA DE IMÁGENES
        lista_imagenes.sort(key=lambda x: int(re.search(r'img_(\d+)', x).group(1)) if re.search(r'img_(\d+)', x) else 0)
        dur_escena = duracion_total / len(lista_imagenes) if lista_imagenes else 0

        for i, img_path in enumerate(lista_imagenes):
            start_t = i * dur_escena
            clip = (ImageClip(img_path)
                    .set_start(start_t)
                    .set_duration(dur_escena)
                    .resize(height=HEIGHT)
                    .set_position("center")
                    .resize(lambda t: 1.03 + 0.07 * (t / dur_escena)))
            
            if viral_mode:
                clip = aplicar_respiracion_asmr_suave(clip)
            
            elementos_video.append(clip)

        # 3. CAPA DE SUBTÍTULOS (con offset dinámico)
        if crear_subtitulos_bloque:
            print(f"   ✍️ Corrigiendo Timestamps con ratio y offset dinámico...")
            try:
                sub_clips = crear_subtitulos_bloque(timestamps_path, palabras_por_bloque=3)
                if sub_clips:
                    duracion_real = duracion_total
                    final_teorico = sub_clips[-1].end
                    ratio = duracion_real / final_teorico if final_teorico > 0 else 1.0

                    # Calcular offset para que el primer bloque aparezca cerca de 0.25s (ajustable)
                    primer_inicio_teorico = sub_clips[0].start
                    primer_inicio_deseado = 0.25  # segundos (puedes cambiarlo)
                    offset = primer_inicio_deseado - (primer_inicio_teorico * ratio)

                    sub_clips_finales = []
                    for s in sub_clips:
                        nuevo_start = (s.start * ratio) + offset
                        nuevo_start = max(0, nuevo_start)
                        nueva_duracion = s.duration * ratio
                        sc = s.set_start(nuevo_start).set_duration(nueva_duracion)
                        sub_clips_finales.append(sc)

                    elementos_video.extend(sub_clips_finales)
                    print(f"   ✅ Ratio: {ratio:.4f} | Offset dinámico: {offset:.4f}")
            except Exception as e:
                print(f"   ⚠️ Error en subtítulos: {e}")

        # 4. OVERLAY DE MÉTRICAS
        if viral_mode and os.path.exists(MAGICK_PATH):
            vistas = f"👁 {np.random.randint(5000, 12000):,} viendo ahora"
            try:
                overlay = (TextClip(vistas, fontsize=42, color='white', font='Arial-Bold', 
                                    stroke_color='black', stroke_width=2, method='label')
                          .set_duration(duracion_total)
                          .set_position(('center', 200))
                          .set_opacity(0.85))
                elementos_video.append(overlay)
            except:
                pass

        # 5. BARRA DE PROGRESO NEÓN
        print("   📊 Añadiendo Barra Neón 2026...")
        barra_neon = crear_barra_progreso_neon_2026(duracion_total)
        elementos_video.append(barra_neon)

        # 6. COMPOSICIÓN Y EXPORTACIÓN
        video_final = CompositeVideoClip(elementos_video, size=(WIDTH, HEIGHT))
        video_final = video_final.set_audio(audio_final).set_duration(duracion_total)

        print(f"🚀 Iniciando Exportación Final...")
        video_final.write_videofile(
            output_path,
            fps=FPS,
            codec="libx264",
            audio_codec="aac",
            threads=12,
            preset="ultrafast"
        )

        audio_final.close()
        video_final.close()
        print(f"✅ ¡Video listo! Tiempo: {time.time() - inicio_proceso:.1f}s")
        return True

    except Exception as e:
        print(f"❌ Error Crítico: {e}")
        return False