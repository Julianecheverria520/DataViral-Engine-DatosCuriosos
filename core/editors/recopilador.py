import os
import numpy as np

# ==========================================================
# PARCHE GLOBAL PARA COMPATIBILIDAD CON PILLOW >=10
# DEBE IR ANTES DE CUALQUIER IMPORT DE MOVIEPY
# ==========================================================
import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS

# Ahora importamos moviepy (ya con el parche aplicado)
from moviepy.editor import VideoFileClip, concatenate_videoclips, CompositeVideoClip

def crear_recopilado_horizontal(lista_videos, output_path):
    """
    Toma videos 9:16 y los une en un 16:9 con Opening y fondo negro (sin desenfoque).
    """
    W_HORIZ, H_HORIZ = 1920, 1080
    PATH_OPENING = "assets/branding/opening_pulsocurioso.mp4"
    clips_procesados = []

    print("🎬 Iniciando Recopilado Pro de PulsoCurioso...")

    # 1. Procesar el Opening (si existe)
    if os.path.exists(PATH_OPENING):
        print("🔔 Integrando Opening...")
        try:
            opening = VideoFileClip(PATH_OPENING).resize(height=H_HORIZ).set_position("center")
            opening_final = CompositeVideoClip([opening], size=(W_HORIZ, H_HORIZ))
            clips_procesados.append(opening_final)
        except Exception as e:
            print(f"⚠️ Error en opening: {e}")
    else:
        print(f"⚠️ Opening no encontrado en {PATH_OPENING}. Continuando sin opening.")

    # 2. Procesar cada video de la lista (fondo negro, sin desenfoque)
    for i, path in enumerate(lista_videos):
        if not os.path.exists(path):
            print(f"⚠️ Video {i+1} no encontrado: {path}")
            continue

        print(f"   Procesando video {i+1}: {os.path.basename(path)}")
        try:
            clip = VideoFileClip(path)
            # Redimensionar manteniendo altura (para que se vea completo en vertical)
            clip_centrado = clip.resize(height=H_HORIZ).set_position("center")
            # Crear un fondo negro del tamaño exacto
            clip_final = CompositeVideoClip([clip_centrado], size=(W_HORIZ, H_HORIZ))
            clips_procesados.append(clip_final)
        except Exception as e:
            print(f"   ❌ Error procesando {path}: {e}")
            import traceback
            traceback.print_exc()
            continue

    # 3. Concatenar y Exportar
    if not clips_procesados:
        print("❌ No hay clips para procesar. Abortando.")
        return False

    print(f"🔗 Concatenando {len(clips_procesados)} clips...")
    try:
        video_final = concatenate_videoclips(clips_procesados, method="compose")
        
        print(f"🚀 Exportando RECAP Horizontal a: {output_path}")
        video_final.write_videofile(
            output_path, 
            fps=30, 
            codec="libx264", 
            audio_codec="aac",
            temp_audiofile='temp-audio.m4a', 
            remove_temp=True,
            threads=8,
            preset="medium"
        )
        print("✅ Recopilado completado exitosamente.")
        return True
    except Exception as e:
        print(f"❌ Error durante la exportación: {e}")
        traceback.print_exc()
        return False