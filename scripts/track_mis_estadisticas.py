"""
track_mis_estadisticas.py - Estadísticas reales del canal de YouTube (YouTube Data API v3).
Equivale a: python main.py STATS
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.tools.youtube_stats import rastrear_estadisticas

if __name__ == "__main__":
    rastrear_estadisticas("@datoscuriososmundo520")
