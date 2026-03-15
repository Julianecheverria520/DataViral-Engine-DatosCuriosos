import os
import sys

# Mostrar información de depuración
print("📂 Directorio actual:", os.getcwd())
ruta_editors = os.path.join("core", "editors")
print("🔍 Buscando módulo en:", os.path.abspath(ruta_editors))

if not os.path.exists(ruta_editors):
    print(f"❌ No existe la carpeta: {ruta_editors}")
    print("   Crea la carpeta 'editors' dentro de 'core' y coloca allí el archivo recopilador.py")
    sys.exit(1)

archivo_recopilador = os.path.join(ruta_editors, "recopilador.py")
if not os.path.exists(archivo_recopilador):
    print(f"❌ No se encuentra el archivo: {archivo_recopilador}")
    sys.exit(1)

# Agregar la raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from core.editors.recopilador import crear_recopilado_horizontal
    print("✅ Motor cargado correctamente.")
except Exception as e:
    print(f"❌ Error al cargar el motor: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# --- CONFIGURACIÓN DE RUTAS ---
carpeta_base = os.path.join("output", "videos")
nombre_final = "ESPECIAL_ESPIRITUALIDAD_VIDAS_PASADAS.mp4"
output_full_path = os.path.join("output", nombre_final)

nombres_archivos = [
    "Almas_gemelas_y_el_reconocimiento_de_hil_30s_Final.mp4",
    "Bebes_que_eligen_a_sus_padres_antes_de_n_30s_Final.mp4",
    "Casos_reales_de_niños_con_recuerdos_de_v_30s_Final.mp4",
    "El_proposito_del_olvido_y_la_eternidad_d_60s_Final.mp4"
]

videos_validos = []
for n in nombres_archivos:
    ruta = os.path.join(carpeta_base, n)
    if os.path.exists(ruta):
        videos_validos.append(ruta)
    else:
        print(f"⚠️ Video no encontrado: {ruta}")

if __name__ == "__main__":
    if videos_validos:
        print(f"🚀 Procesando {len(videos_validos)} videos...")
        crear_recopilado_horizontal(videos_validos, output_full_path)
    else:
        print("⚠️ No se encontraron videos. Revisa la carpeta output/videos")