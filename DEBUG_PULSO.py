import os
import sys

# Forzamos que los prints salgan de inmediato
print("--- TEST DE EMERGENCIA PULSO CURIOSO ---")
print(f"Directorio actual: {os.getcwd()}")

try:
    import PIL.Image
    if not hasattr(PIL.Image, 'ANTIALIAS'):
        PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS
    print("✅ Pillow: OK")
    
    from moviepy.editor import VideoFileClip, concatenate_videoclips, CompositeVideoClip, vfx
    print("✅ MoviePy: OK")
except Exception as e:
    print(f"❌ ERROR CARGANDO LIBRERÍAS: {e}")
    sys.exit()

def test_rapido():
    # Ruta a tus videos (Ajustada a lo que me mostraste)
    carpeta_videos = os.path.join("output", "videos")
    video_test = os.path.join(carpeta_videos, "Almas_gemelas_y_el_reconocimiento_de_hil_30s_Final.mp4")
    
    if not os.path.exists(video_test):
        print(f"⚠️ No encontré el video en: {video_test}")
        return

    print(f"🚀 Intentando procesar un clip de prueba...")
    try:
        clip = VideoFileClip(video_test).subclip(0, 5) # Solo 5 segundos para test
        # Redimensionar usando el método que NO falla
        final = clip.fx(vfx.resize, width=1920)
        final.write_videofile("TEST_HORIZONTAL.mp4", fps=24, codec="libx264")
        print("✨ ¡TEST EXITOSO! Se creó TEST_HORIZONTAL.mp4")
    except Exception as e:
        print(f"❌ ERROR EN EL RENDER: {e}")

if __name__ == "__main__":
    test_rapido()