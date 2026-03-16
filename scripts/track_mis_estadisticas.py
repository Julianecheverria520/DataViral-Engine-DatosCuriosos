import sys
import os
sys.path.append(os.path.dirname(__file__))

from core.tools.stats_tracker import TikTokStatsTracker  # aunque el nombre diga TikTok, funciona igual

def main():
    # URL de tu canal de YouTube
    url = "https://www.youtube.com/@datoscuriososmundo520"
    
    tracker = TikTokStatsTracker(headless=True)  # headless=True para que no se abra ventana
    try:
        tracker.start_driver()
        # Para YouTube, necesitas cambiar los selectores dentro del método track_profile
        # Por ahora, podrías sobreescribir el método o crear uno específico
        # Aquí llamamos al método genérico (pero no funcionará sin adaptar)
        data = tracker.track_profile(url)
        print("Datos obtenidos:", data)
    finally:
        tracker.close_driver()

if __name__ == "__main__":
    main()