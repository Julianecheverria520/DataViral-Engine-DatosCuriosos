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
    from core.editors.efectos import crear_subtitulos_bloque
    from core.editors.branding import insertar_popup_suscripcion # <-- NUEVA MEJORA DE MARCA
    print("✅ Módulos de efectos y branding cargados con éxito")
except ImportError:
    print("⚠️ Módulos secundarios no encontrados. Continuando con motor básico.")
    crear_subtitulos_bloque = None
    insertar_popup_suscripcion = None

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

        # 2. CAPA DE IMÁGENES (CON ZOOM ALTERNADO ASIMÉTRICO)
        lista_imagenes.sort(key=lambda x: int(re.search(r'img_(\d+)', x).group(1)) if re.search(r'img_(\d+)', x) else 0)
        dur_escena = duracion_total / len(lista_imagenes) if lista_imagenes else 0

        for i, img_path in enumerate(lista_imagenes):
            start_t = i * dur_escena
            
            # DINAMISMO: Escenas pares Zoom In, Impares Zoom Out
            if i % 2 == 0:
                animacion = lambda t: 1.0 + 0.08 * (t / dur_escena)
            else:
                animacion = lambda t: 1.08 - 0.08 * (t / dur_escena)

            clip = (ImageClip(img_path)
                    .set_start(start_t)
                    .set_duration(dur_escena)
                    .resize(height=HEIGHT)
                    .set_position("center")
                    .resize(animacion))
            
            # Efecto de pulso especial solo para el Hook (Escena 1)
            if i == 0 and viral_mode:
                clip = clip.resize(lambda t: 1.0 + 0.04 * np.sin(2 * np.pi * 0.5 * t))
            elif viral_mode:
                clip = aplicar_respiracion_asmr_suave(clip)
            
            elementos_video.append(clip)

        # 3. CAPA DE SUBTÍTULOS (Sincronía Instantánea)
        if crear_subtitulos_bloque:
            print(f"   ✍️ Corrigiendo Timestamps con ratio y offset dinámico...")
            try:
                sub_clips = crear_subtitulos_bloque(timestamps_path, palabras_por_bloque=3)
                if sub_clips:
                    duracion_real = duracion_total
                    final_teorico = sub_clips[-1].end
                    ratio = duracion_real / final_teorico if final_teorico > 0 else 1.0

                    # Offset de 0.05s para que el texto aparezca casi al frame 1
                    primer_inicio_teorico = sub_clips[0].start
                    primer_inicio_deseado = 0.05 
                    offset = primer_inicio_deseado - (primer_inicio_teorico * ratio)

                    sub_clips_finales = []
                    for s in sub_clips:
                        nuevo_start = max(0, (s.start * ratio) + offset)
                        nueva_duracion = s.duration * ratio
                        sc = s.set_start(nuevo_start).set_duration(nueva_duracion)
                        sub_clips_finales.append(sc)

                    elementos_video.extend(sub_clips_finales)
                    print(f"   ✅ Ratio: {ratio:.4f} | Offset: {offset:.4f}")
            except Exception as e:
                print(f"   ⚠️ Error en subtítulos: {e}")

        # 4. OVERLAY DE MÉTRICAS (Social Proof)
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

        # 5. INTEGRACIÓN DE MARCA DINÁMICA (Pop-up Suscríbete)
        if insertar_popup_suscripcion:
            elementos_video = insertar_popup_suscripcion(elementos_video, duracion_total, WIDTH, HEIGHT)

        # 6. BARRA DE PROGRESO NEÓN
        barra_neon = crear_barra_progreso_neon_2026(duracion_total)
        elementos_video.append(barra_neon)

        # 7. COMPOSICIÓN Y EXPORTACIÓN
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