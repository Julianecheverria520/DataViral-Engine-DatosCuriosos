import openai
import os
import json
from dotenv import load_dotenv

# AJUSTE DE RUTA MODULAR:
# Ahora que estamos dentro de core/engines, apuntamos a la nueva ubicación de tools
try:
    from core.tools.hooks_engine import generar_hook_controlado
except ImportError:
    # Backup por si se ejecuta el archivo de forma aislada
    import sys
    ruta_raiz = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if ruta_raiz not in sys.path:
        sys.path.insert(0, ruta_raiz)
    from core.tools.hooks_engine import generar_hook_controlado

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def obtener_guion_y_prompts_visuales(tema, segundos=30, modo="normal", canal="misterio", hook_externo=None, feedback=""):
    print(f"🧠 MOTOR ESTRATÉGICO | {tema} | {segundos}s")

    # --- LÓGICA DE MEMORIA DE ERRORES ---
    lecciones_contexto = ""
    path_memoria = "memoria_errores.json"
    if os.path.exists(path_memoria):
        try:
            with open(path_memoria, "r", encoding="utf-8") as f:
                memoria = json.load(f)
                lecciones = memoria.get("lecciones_aprendidas", [])
                lecciones_contexto = "\n".join([f"- {l}" for l in lecciones])
        except Exception as e:
            print(f"⚠️ No se pudo leer la memoria de errores: {e}")

    # --- AJUSTE DE EXTENSIÓN ---
    if segundos <= 35:
        num_escenas = 4
        min_p, max_p = 60, 75
    else:
        num_escenas = 8
        min_p, max_p = 140, 165

    hook_final = hook_externo if hook_externo else generar_hook_controlado(tema, canal)

    # --- PROMPT CON INYECCIÓN DE APRENDIZAJE ---
    prompt_sistema = f"""
    Eres un guionista senior de documentales virales. Tu misión es la perfección narrativa.

    ⚠️ LECCIONES CRÍTICAS DE PROYECTOS ANTERIORES (NO FALLAR AQUÍ):
    {lecciones_contexto}

    ⚠️ REGLAS DE SESIÓN:
    - Longitud: Entre {min_p} y {max_p} palabras totales.
    - Contenido: Cero relleno. Solo datos duros, nombres y tecnicismos.
    - Cámaras: Alterna entre [Extreme Close-up, Wide Shot, Macro, Low Angle]. No repitas lentes.

    --- INTEGRIDAD ---
    - ESCENA 1 DEBE SER: "{hook_final}"

    FORMATO JSON OBLIGATORIO:
    {{
      "guion": [
        {{ "escena": 1, "texto": "{hook_final}", "palabra_clave": "...", "prompt_imagen": "[Sujeto] + [Contexto] + [Luz] + [Cámara] + [Calidad]" }},
        ... (total {num_escenas} escenas)
      ],
      "titulo_redes": "...",
      "hashtags": [...]
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": prompt_sistema}, 
                {"role": "user", "content": f"Tema: {tema}. Feedback adicional: {feedback}"}
            ],
            response_format={"type": "json_object"}
        )
        data = json.loads(response.choices[0].message.content)
        data["guion"][0]["texto"] = hook_final
        return data, hook_final
    except Exception as e:
        print(f"❌ Error GPT: {e}")
        return None, hook_final