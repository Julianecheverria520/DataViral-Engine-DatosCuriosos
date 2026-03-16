import openai
import os
import json
import random
from dotenv import load_dotenv

# Importación modular corregida
try:
    from core.tools.hooks_engine import generar_hook_controlado
except ImportError:
    import sys
    ruta_raiz = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if ruta_raiz not in sys.path:
        sys.path.insert(0, ruta_raiz)
    from core.tools.hooks_engine import generar_hook_controlado

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- UTILIDADES DE APOYO ---
def cargar_memoria(archivo, clave):
    if os.path.exists(archivo):
        try:
            with open(archivo, "r", encoding="utf-8") as f:
                memoria = json.load(f)
                return memoria.get(clave, [])
        except:
            return []
    return []

def distribuir_tiempo(total_segundos, num_escenas):
    """Distribuye el tiempo: primera y última cortas, centrales más largas."""
    if num_escenas == 5:
        proporcion = [0.12, 0.18, 0.25, 0.25, 0.20] # Patrón piramidal
    else:
        proporcion = [1/num_escenas] * num_escenas
    return [max(2, round(total_segundos * p)) for p in proporcion]

# --- MOTOR PRINCIPAL V2 ---
def obtener_guion_y_prompts_visuales(tema, segundos=30, modo="normal", canal="misterio", hook_externo=None, feedback=""):
    print(f"🧠 MOTOR ESTRATÉGICO V2 | {tema} | {segundos}s | canal: {canal}")

    # 1. Memoria de aciertos y errores (Doble vía)
    lecciones = cargar_memoria("memoria_errores.json", "lecciones_aprendidas")
    aciertos = cargar_memoria("memoria_aciertos.json", "patrones_exitosos")
    
    contexto_aprendizaje = ""
    if lecciones:
        contexto_aprendizaje += "⚠️ ERRORES A EVITAR:\n" + "\n".join([f"- {l}" for l in lecciones]) + "\n"
    if aciertos:
        contexto_aprendizaje += "✅ PATRONES QUE FUNCIONAN:\n" + "\n".join([f"- {a}" for a in aciertos]) + "\n"

    # 2. Estructura de Tiempo
    num_escenas = 5 
    tiempos = distribuir_tiempo(segundos, num_escenas)

    # 3. Hook Viral
    hook = hook_externo if hook_externo else generar_hook_controlado(tema, canal)

    # 4. Prompt Maestro
    prompt_sistema = f"""
    Eres un guionista senior de documentales virales para {canal}. Tu misión es la perfección narrativa.
    Crearás un guion de {segundos}s dividido en 5 actos para retención máxima.

    ## ESTRUCTURA DE 5 ACTOS:
    1. HOOK ({tiempos[0]}s): Debe ser exactamente: "{hook}"
    2. CONTEXTO ({tiempos[1]}s): Ejemplo concreto o antecedente real.
    3. DESARROLLO ({tiempos[2]}s): La ciencia/mecanismo con tecnicismos.
    4. CLÍMAX ({tiempos[3]}s): Giro inesperado o paradoja.
    5. LOOP/CTA ({tiempos[4]}s): Vuelve al inicio para crear un bucle infinito.

    ## ESTILO:
    - 1.5 palabras por segundo. Frases potentes.
    - Datos duros, años, nombres científicos.
    - Prompts de imagen: "[Sujeto] + [Contexto] + [Luz] + [Cámara] + [Estilo {canal}] + 8k"

    ## APRENDIZAJE:
    {contexto_aprendizaje}

    FORMATO JSON:
    {{
      "guion": [
        {{ "escena": 1, "texto": "{hook}", "palabra_clave": "...", "prompt_imagen": "..." }},
        ...
      ],
      "titulo_redes": "...", "hashtags": [...]
    }}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": f"Tema: {tema}. Feedback: {feedback}"}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        data = json.loads(response.choices[0].message.content)
        data["guion"][0]["texto"] = hook
        
        # Lógica de Loop forzado
        ultimo_texto = data["guion"][-1]["texto"]
        if hook.lower() not in ultimo_texto.lower():
            data["guion"][-1]["texto"] += f" Por eso, siempre volvemos a preguntarnos: {hook}"
        
        return data, hook
    except Exception as e:
        print(f"❌ Error GPT V2: {e}")
        return None, hook