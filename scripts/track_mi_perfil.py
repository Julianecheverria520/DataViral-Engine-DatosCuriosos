"""
track_mi_perfil.py - Solo trackea el perfil.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.tools.stats_tracker import trackear_perfil_tiktok

trackear_perfil_tiktok("https://www.tiktok.com/@datoscuriososmundo520", headless=True)