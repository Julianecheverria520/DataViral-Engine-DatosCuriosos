import openai
import os
import json
from dotenv import load_dotenv

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def obtener_guion_y_prompts_visuales(tema, segundos=30):
    print(f"🧠 INGENIERÍA DE RETENCIÓN ACTIVADA: {tema} ({segundos}s)")

    # ----------------------------
    # DENSIDAD SEGÚN DURACIÓN
    # ----------------------------
    if segundos <= 45:
        num_escenas = 5
        palabras_por_escena = "10 a 14"
    elif segundos <= 90:
        num_escenas = 8
        palabras_por_escena = "14 a 18"
    else:
        num_escenas = 12
        palabras_por_escena = "18 a 24"

    prompt_sistema = f"""
Eres un ARQUITECTO de retención viral para contenido vertical tipo TikTok.

Tu objetivo no es informar.
Tu objetivo es RETENER.

IDENTIDAD DEL CANAL:
- Misterioso
- Oscuro
- Serio
- Impactante
- Sensación de secreto revelado

ESTRUCTURA DE TENSIÓN:

ESCENA 1:
Hook disruptivo.
Advertencia o comparación extrema.
Generar curiosidad inmediata.

ESCENAS INTERMEDIAS:
Escalada progresiva.
Cada escena empeora la anterior.
Crear micro-loops sin cerrar completamente la idea.

CLÍMAX:
Revelación fuerte.
Impacto psicológico.

FINAL:
Pregunta o dilema que genere comentarios.

CONFIGURACIÓN:
Duración objetivo: {segundos} segundos.
Número de escenas: {num_escenas}
Extensión por escena: {palabras_por_escena}

REGLAS CRÍTICAS:

Cada escena debe tener EXACTAMENTE:
- texto
- palabra_clave (UNA sola palabra emocional potente)
- prompt_imagen

REGLAS PARA prompt_imagen (OBLIGATORIO):

El prompt_imagen debe describir visualmente la escena con:

1) Tipo de plano (close-up, wide shot, aerial, medium shot, etc.)
2) Ubicación específica (ciudad, interior, calle, edificio, etc.)
3) Personaje con edad aproximada
4) Emoción visible en el rostro o cuerpo
5) Acción concreta en progreso
6) Hora del día
7) Ambiente/clima
8) Sensación cinematográfica realista

Debe ser altamente descriptivo.
Debe ser generable por IA visual.
No usar solo estilos como "dark cinematic lighting".
No repetir exactamente la misma estructura entre escenas.
No usar frases genéricas.

TEXTO:
- Frases cortas.
- Ritmo alto.
- No tono documental.
- No explicaciones largas.
- Sensación constante de escalada.

FORMATO JSON OBLIGATORIO:

{{
  "tipo_contenido": "Impacto/Misterio/Comparacion",
  "guion": [
    {{
      "escena": 1,
      "texto": "...",
      "palabra_clave": "...",
      "prompt_imagen": "..."
    }}
  ]
}}

Devuelve solo JSON válido.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": f"Tema: {tema}"}
            ],
            response_format={"type": "json_object"}
        )

        data = json.loads(response.choices[0].message.content)

        # Validación básica
        if "guion" not in data:
            raise ValueError("JSON sin guion")

        return data

    except Exception as e:
        print(f"❌ Error en GPT Engine: {e}")
        return None