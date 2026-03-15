import os
from moviepy.editor import VideoFileClip, vfx

def insertar_popup_suscripcion(elementos_video, duracion_total, width, height):
    """
    Inserta el mini-video de suscripción eliminando el fondo verde puro.
    Posicionamiento optimizado para no interferir con subtítulos.
    """
    path_video_sub = "assets/branding/clic_animado.mp4"
    
    if not os.path.exists(path_video_sub):
        print(f"⚠️ No se encontró {path_video_sub}. Continuando sin branding.")
        return elementos_video

    print("🔔 Aplicando Chroma Key (Verde Puro) y ajustando posición...")
    
    try:
        # 1. Cargamos el mini-video
        video_sub = VideoFileClip(path_video_sub)
        
        # 2. CHROMA KEY DIRECTO
        # Al ser verde puro, usamos [0, 255, 0]. 
        # Mantengo thr=100 para asegurar que las chispas y bordes de la mano queden limpios.
        video_sub = video_sub.fx(vfx.mask_color, color=[0, 255, 0], thr=100, s=5)
        
        # 3. CONFIGURACIÓN DE TIEMPO
        # Aparece al 75% del video
        tiempo_inicio = duracion_total * 0.65
        
        # 4. POSICIONAMIENTO Y TAMAÑO
        video_sub = (video_sub.set_start(tiempo_inicio)
                    .set_duration(4) # Duración ideal para ver el movimiento y el clic
                    .resize(width=520) # Tamaño con buen impacto visual
                    # POSICIÓN ELEVADA: 'height - 950' lo ubica en la zona central-alta.
                    # Esto evita CUALQUIER solapamiento con subtítulos o la barra neón.
                    .set_position(("center", height - 950)))

        elementos_video.append(video_sub)
        print("   ✅ Pop-up 'PulsoCurioso' listo en la capa superior.")
        return elementos_video

    except Exception as e:
        print(f"❌ Error en branding.py: {e}")
        return elementos_video