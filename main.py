import json
import os
import sys
import re

# ==========================================================
# CONFIGURACIÓN GLOBAL
# ==========================================================
os.environ["IMAGEIO_FFMPEG_EXE"] = r"C:\ffmpeg\bin\ffmpeg.exe"

BASE_DIR = "proyectos"
OUTPUT_DIR = os.path.join("output", "videos")

# ==========================================================
# PROTOCOLO DE CONEXIÓN DE MÓDULOS
# ==========================================================
ruta_raiz = os.path.dirname(os.path.abspath(__file__))
ruta_core = os.path.join(ruta_raiz, "core")

if ruta_raiz not in sys.path:
    sys.path.insert(0, ruta_raiz)

if ruta_core not in sys.path:
    sys.path.insert(0, ruta_core)

try:
    from core.gpt_engine import obtener_guion_y_prompts_visuales
    from core.voice_engine import generar_voz
    from core.image_engine import generar_imagen
    from core.video_editor import crear_video_pro_con_imagenes
except Exception as e:
    print(f"❌ Error importando módulos: {e}")
    sys.exit(1)

# ==========================================================
# UTILIDADES
# ==========================================================
def limpiar_nombre_carpeta(nombre):
    return re.sub(r'[\\/*?:"<>|]', "", nombre).strip().replace(' ', '_')

def limpiar_texto_etiquetas(texto):
    return re.sub(r'\[.*?\]', '', texto).strip()

# ==========================================================
# FASE 1: PREPARAR
# ==========================================================
def fase_preparar(tema, segundos, modo, canal):

    os.makedirs(BASE_DIR, exist_ok=True)

    tema_limpio = limpiar_nombre_carpeta(tema[:40])
    path = os.path.join(BASE_DIR, f"{tema_limpio}_{segundos}s")
    img_folder = os.path.join(path, "images")

    os.makedirs(path, exist_ok=True)
    os.makedirs(img_folder, exist_ok=True)

    print(f"\n🚀 GENERANDO PROYECTO: {tema} ({segundos}s) | MODO: {modo} | CANAL: {canal}")

    # CAMBIO: Ahora enviamos el cuarto parámetro 'canal'
    datos = obtener_guion_y_prompts_visuales(tema, segundos, modo=modo, canal=canal)

    if not datos or "guion" not in datos:
        print("❌ GPT no devolvió guion válido.")
        return

    # Guardar guion
    guion_path = os.path.join(path, "guion.json")
    with open(guion_path, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)

    # Generar audio + timestamps
    texto_completo = " ".join(
        limpiar_texto_etiquetas(e["texto"]) for e in datos["guion"]
    )

    audio_path = os.path.join(path, "audio.mp3")
    timestamps_path = os.path.join(path, "timestamps.json")
    
    exito_voz = generar_voz(texto_completo, audio_path, timestamps_path)

    if not exito_voz:
        print("❌ Fallo generando audio.")
        return

    # Generar imágenes
    for idx, escena in enumerate(datos["guion"]):
        img_path = os.path.join(img_folder, f"img_{idx}.png")

        if not os.path.exists(img_path):
            print(f"🎨 Generando imagen {idx+1}/{len(datos['guion'])}")
            generar_imagen(escena["prompt_imagen"], img_path)

    print(f"\n✅ PROYECTO LISTO EN: {path}")

# ==========================================================
# FASE 2: MONTAR
# ==========================================================
def fase_montar():

    if not os.path.exists(BASE_DIR):
        print("❌ No existe la carpeta proyectos.")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    proyectos = [
        d for d in os.listdir(BASE_DIR)
        if os.path.isdir(os.path.join(BASE_DIR, d))
    ]

    if not proyectos:
        print("⚠ No hay proyectos para montar.")
        return

    for p in proyectos:

        path_p = os.path.join(BASE_DIR, p)
        guion_p = os.path.join(path_p, "guion.json")
        audio_p = os.path.join(path_p, "audio.mp3")
        timestamps_p = os.path.join(path_p, "timestamps.json")
        img_f = os.path.join(path_p, "images")
        output_v = os.path.join(OUTPUT_DIR, f"{p}_Final.mp4")

        if os.path.exists(output_v):
            print(f"⏩ Saltando {p} (ya renderizado)")
            continue

        if not (os.path.exists(guion_p) and os.path.exists(audio_p) and os.path.exists(timestamps_p)):
            print(f"⚠ Proyecto incompleto: {p}")
            continue

        print(f"\n🎬 MONTANDO: {p}")

        with open(guion_p, "r", encoding="utf-8") as f:
            datos = json.load(f)

        if "guion" not in datos:
            print("❌ Guion inválido.")
            continue

        # Limpiar textos
        for escena in datos["guion"]:
            escena["texto"] = limpiar_texto_etiquetas(escena["texto"])

        # Recolectar imágenes ordenadas
        if not os.path.exists(img_f):
            print("❌ Carpeta imágenes no encontrada.")
            continue

        imagenes = [
            os.path.join(img_f, f)
            for f in os.listdir(img_f)
            if f.endswith(".png")
        ]

        if not imagenes:
            print("❌ No hay imágenes.")
            continue

        imagenes.sort(
            key=lambda x: int(re.search(r'img_(\d+)', x).group(1))
        )

        try:
            crear_video_pro_con_imagenes(
                datos["guion"],
                audio_p,
                timestamps_p,
                imagenes,
                output_v
            )

            print(f"⭐ VIDEO GENERADO: {output_v}")

        except Exception as e:
            print(f"❌ Error montando {p}: {e}")

# ==========================================================
# FASE 3: STATS
# ==========================================================
def fase_estadisticas():
    print("\n📊 ESTADO DEL MOTOR")
    print("Sistema operativo")
    print("Render engine activo")
    print("Modo viral optimizado")

# ==========================================================
# ENTRY POINT
# ==========================================================
if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("\nUso:")
        print("python main.py PREPARAR 'Tema' 45 'agresivo' 'misterio'")
        print("python main.py MONTAR")
        sys.exit(0)

    modo_sistema = sys.argv[1].upper()

    if modo_sistema == "PREPARAR":
        tema = sys.argv[2] if len(sys.argv) > 2 else input("Tema: ")
        segundos = int(sys.argv[3]) if len(sys.argv) > 3 else 30
        modo_gpt = sys.argv[4] if len(sys.argv) > 4 else "normal" 
        canal_gpt = sys.argv[5] if len(sys.argv) > 5 else "misterio"
        fase_preparar(tema, segundos, modo_gpt, canal_gpt)

    elif modo_sistema == "MONTAR":
        fase_montar()

    elif modo_sistema == "STATS":
        fase_estadisticas()