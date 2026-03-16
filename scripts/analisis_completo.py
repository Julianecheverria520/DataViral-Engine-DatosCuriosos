"""
analisis_completo.py - Ejecuta el análisis completo del perfil y videos recientes.
"""
import sys
import os

# Asegurar que podemos importar desde core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.tools.stats_tracker import trackear_perfil_tiktok, analizar_videos_recientes

def main():
    # 1. Estadísticas del perfil
    perfil = trackear_perfil_tiktok("https://www.tiktok.com/@datoscuriososmundo520", headless=True)
    print("Perfil:", perfil)

    # 2. Análisis de últimos videos (sin entrar a cada video para evitar bloqueos)
    # Si quieres ver el navegador, cambia headless=False
    videos = analizar_videos_recientes("https://www.tiktok.com/@datoscuriososmundo520", max_videos=10, headless=True)
    print(f"Se analizaron {len(videos)} videos")

if __name__ == "__main__":
    main()