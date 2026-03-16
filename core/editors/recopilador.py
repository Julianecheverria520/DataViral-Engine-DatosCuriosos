import os
import numpy as np  # <--- IMPORTANTE: Declarado aquí arriba
import PIL.Image
import PIL.ImageFilter

# Parche de compatibilidad para MoviePy/Pillow
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS

from moviepy.editor import VideoFileClip, concatenate_videoclips, CompositeVideoClip, ColorClip, vfx

def aplicar_desenfoque(image):
    """
    Transforma el frame a Pillow, aplica desenfoque y lo devuelve a NumPy.
    """
    pil_img = PIL.Image.fromarray(image)
    # 40 es un radio de desenfoque ideal para el efecto Glow
    blurred_img = pil_img.filter(PIL.ImageFilter.GaussianBlur(radius=40))
    return np.array(blurred_img)

def crear_recopilado_horizontal(lista_videos, output_path):
    W_HORIZ, H_HORIZ = 1920, 1080
    PATH_OPENING = "assets/branding/opening_pulsocurioso.mp4"
    clips_procesados = []

    print("\n" + "="*40)
    print("🎬 MOTOR PULSOCURIOSO: MODO HORIZONTAL GLOW")
    print("="*40)

    # 1. Integración del Opening
    if os.path.exists(PATH_OPENING):
        print(f"🔔 Cargando Opening...")
        try:
            op = VideoFileClip(PATH_OPENING).fx(vfx.resize, height=H_HORIZ).set_position("center")
            fondo_op = ColorClip((W_HORIZ, H_HORIZ), (0,0,0)).set_duration(op.duration)
            clips_procesados.append(CompositeVideoClip([fondo_op, op]))
        except Exception as e:
            print(f"⚠️ Error en opening: {e}")

    # 2. Procesamiento de Clips con Resplandor
    for i, path in enumerate(lista_videos, 1):
        try:
            print(f"🎥 [{i}/{len(lista_videos)}] Aplicando Glow: {os.path.basename(path)}")
            clip_v = VideoFileClip(path).fx(vfx.resize, height=H_HORIZ).set_position("center")
            
            # --- CAPA DE RESPLANDOR (GLOW) ---
            # Escalamos el video un poco más para que el resplandor sobresalga
            resplandor = (clip_v.fx(vfx.resize, width=int(W_HORIZ * 1.2))
                          .fl_image(aplicar_desenfoque)
                          .set_opacity(0.3)
                          .set_position("center"))
            
            # Fondo negro base
            fondo_negro = ColorClip(size=(W_HORIZ, H_HORIZ), color=[0, 0, 0]).set_duration(clip_v.duration)
            
            # Composición de capas: Fondo -> Glow -> Video Original
            escena = CompositeVideoClip([fondo_negro, resplandor, clip_v], size=(W_HORIZ, H_HORIZ))
            clips_procesados.append(escena)
            
        except Exception as e:
            print(f"❌ Error en clip {i}: {e}")

    # 3. Renderizado Final
    if clips_procesados:
        print("\n⚡ Iniciando Renderizado Final... (Paciencia, el Glow es pesado)")
        video_final = concatenate_videoclips(clips_procesados, method="compose")
        
        try:
            video_final.write_videofile(
                output_path, 
                fps=30, 
                codec="libx264", 
                audio_codec="aac",
                threads=8,
                logger='bar'
            )
            print(f"\n✨ ¡RECOPILADO TERMINADO! Guardado en: {output_path}")
            return True
        except Exception as e:
            print(f"\n❌ Falló el renderizado: {e}")
            return False
    return False