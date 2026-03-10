import json
import os
import sys
import re
import time
import random
from core.limpieza_engine import limpiar_texto_para_tts, insertar_pausas_inteligentes

# ==========================================================
# CONFIGURACIÓN GLOBAL
# ==========================================================
os.environ["IMAGEIO_FFMPEG_EXE"] = r"C:\ffmpeg\bin\ffmpeg.exe"
BASE_DIR = "proyectos"
OUTPUT_DIR = os.path.join("output", "videos")
MUSIC_DIR = "assets/music" 

ruta_raiz = os.path.dirname(os.path.abspath(__file__))
if ruta_raiz not in sys.path:
    sys.path.insert(0, ruta_raiz)

try:
    from core.gpt_engine import obtener_guion_y_prompts_visuales
    from core.auditor_engine import auditar_guion
    from core.hooks_engine import generar_hook_controlado
    from core.voice_engine import generar_voz
    from core.video_editor import crear_video_pro_con_imagenes
except Exception as e:
    print(f"❌ Error importando módulos core: {e}"); sys.exit(1)

# ==========================================================
# UTILIDADES
# ==========================================================
def obtener_musica_por_canal(canal):
    folder = os.path.join(MUSIC_DIR, canal.lower())
    if os.path.exists(folder):
        archivos = [f for f in os.listdir(folder) if f.endswith(".mp3")]
        if archivos:
            return os.path.join(folder, random.choice(archivos))
    return None

def limpiar_nombre_carpeta(nombre):
    return re.sub(r'[\\/*?:"<>|]', "", nombre).strip().replace(' ', '_')

def extraer_indice(ruta):
    match = re.search(r'img_(\d+)', ruta)
    return int(match.group(1)) if match else 9999

# ==========================================================
# FASE 1: PREPARAR
# ==========================================================
def fase_preparar(tema_original, segundos, modo, canal):
    print(f"\n🧠 --- INICIANDO PREPARACIÓN: {tema_original} ---")
    hook_maestro = generar_hook_controlado(tema_original, canal)
    
    intentos_max = 3
    intento_actual = 0
    guion_aprobado = False
    datos_finales = None
    instruccion_extra = "" 

    while not guion_aprobado and intento_actual < intentos_max:
        intento_actual += 1
        datos_temp, hook_real = obtener_guion_y_prompts_visuales(
            tema_original, segundos, modo, canal, 
            hook_externo=hook_maestro, feedback=instruccion_extra
        )
        if not datos_temp: continue

        revision = auditar_guion(datos_temp, tema_original, hook_real)
        if revision.get("aprobado"):
            datos_finales = datos_temp
            guion_aprobado = True
        else:
            instruccion_extra = revision.get("mejora")
            print(f"⚠️ Intento {intento_actual} rechazado: {revision.get('razon')}")

    if not datos_finales:
        print("❌ No se pudo generar un guion que cumpla los requisitos.")
        return

    tema_limpio = limpiar_nombre_carpeta(tema_original[:40])
    path = os.path.join(BASE_DIR, f"{tema_limpio}_{segundos}s")
    os.makedirs(os.path.join(path, "images"), exist_ok=True)

    datos_finales["canal_meta"] = canal

    audio_path = os.path.join(path, "audio.mp3")
    timestamps_path = os.path.join(path, "timestamps.json")
    
    escenas = datos_finales["guion"]
    texto_para_voz = " ".join([
        insertar_pausas_inteligentes(limpiar_texto_para_tts(e["texto"]), i == len(escenas)-1) 
        for i, e in enumerate(escenas)
    ])

    conteo_p = len(texto_para_voz.split())
    print(f"🎙️ Palabras finales: {conteo_p} | Estimación: {conteo_p/2.2:.1f} segundos.")

    generar_voz(texto_para_voz, audio_path, timestamps_path)

    with open(os.path.join(path, "guion.json"), "w", encoding="utf-8") as f:
        json.dump(datos_finales, f, indent=4, ensure_ascii=False)

    info_path = os.path.join(path, "info_publicacion.txt")
    titulo_redes = datos_finales.get("titulo_redes", tema_original)
    tags = " ".join(datos_finales.get("hashtags", ["#viral", "#insightdatamind"]))
    
    with open(info_path, "w", encoding="utf-8") as f:
        f.write(f"PROYECTO: {tema_original}\n")
        f.write(f"DURACIÓN: {segundos}s\n")
        f.write("-" * 30 + "\n")
        f.write(f"TITULO PARA REDES:\n{titulo_redes}\n\n")
        f.write(f"HASHTAGS:\n{tags}\n")

    print(f"✅ PROYECTO LISTO: {path}")

# ==========================================================
# FASE ESPECIAL: RE-HACER AUDIO (SOLO VOZ Y TIMESTAMPS)
# ==========================================================
def fase_reconstruir_audio(nombre_proyecto):
    """Vuelve a generar el audio.mp3 y timestamps.json usando el guion.json existente."""
    path = os.path.join(BASE_DIR, nombre_proyecto)
    guion_path = os.path.join(path, "guion.json")

    if not os.path.exists(guion_path):
        print(f"❌ Error: No existe guion.json en {path}")
        return

    print(f"🎙️ RE-PROCESANDO VOZ PARA: {nombre_proyecto}")
    with open(guion_path, "r", encoding="utf-8") as f:
        datos = json.load(f)

    texto_para_voz = ""
    escenas = datos["guion"]
    for i, escena in enumerate(escenas):
        t_limpio = limpiar_texto_para_tts(escena["texto"])
        es_ultima = (i == len(escenas) - 1)
        texto_para_voz += insertar_pausas_inteligentes(t_limpio, es_ultima=es_ultima) + " "

    audio_path = os.path.join(path, "audio.mp3")
    timestamps_path = os.path.join(path, "timestamps.json")

    # Limpieza de archivos previos
    if os.path.exists(audio_path): os.remove(audio_path)
    if os.path.exists(timestamps_path): os.remove(timestamps_path)

    generar_voz(texto_para_voz.strip(), audio_path, timestamps_path)
    print(f"✅ Audio y Timestamps reconstruidos exitosamente.")

# ==========================================================
# FASE 2: MONTAR
# ==========================================================
def fase_montar():
    if not os.path.exists(BASE_DIR): return
    proyectos = [d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d))]
    
    for p in proyectos:
        path_p = os.path.join(BASE_DIR, p)
        guion_p = os.path.join(path_p, "guion.json")
        audio_p = os.path.join(path_p, "audio.mp3")
        img_f = os.path.join(path_p, "images")
        output_v = os.path.join(OUTPUT_DIR, f"{p}_Final.mp4")

        if os.path.exists(output_v) or not os.path.exists(guion_p): continue

        with open(guion_p, "r", encoding="utf-8") as f:
            datos_json = json.load(f)

        canal_target = datos_json.get("canal_meta", "misterio")
        musica_path = obtener_musica_por_canal(canal_target)

        imagenes = [os.path.join(img_f, f) for f in os.listdir(img_f) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
        imagenes.sort(key=extraer_indice)

        if len(imagenes) >= len(datos_json["guion"]):
            print(f"🎬 Montando video: {p}")
            crear_video_pro_con_imagenes(
                datos_json, audio_p, os.path.join(path_p, "timestamps.json"), 
                imagenes, output_v, musica_path=musica_path
            )

# ==========================================================
# PUNTO DE ENTRADA
# ==========================================================
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python main.py [PREPARAR | MONTAR | REHACER_AUDIO]")
        sys.exit(0)
    
    cmd = sys.argv[1].upper()
    if cmd == "PREPARAR":
        fase_preparar(sys.argv[2], int(sys.argv[3]), sys.argv[4], sys.argv[5])
    elif cmd == "REHACER_AUDIO":
        fase_reconstruir_audio(sys.argv[2])
    elif cmd == "MONTAR":
        fase_montar()