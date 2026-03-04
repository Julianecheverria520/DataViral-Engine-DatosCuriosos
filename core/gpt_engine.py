import openai
import os
import json
from dotenv import load_dotenv

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def obtener_guion_y_prompts_visuales(tema, segundos=30, modo="normal", canal="misterio"):

    print(f"🧠 MOTOR VIRAL ACTIVADO | MODO: {modo.upper()} | CANAL: {canal.upper()} | {tema} ({segundos}s)")

    # -------------------------------------------------
    # CÁLCULO REAL DE DURACIÓN (≈150 palabras/min)
    # -------------------------------------------------
    palabras_objetivo = int(segundos * 2.5)

    # Distribución inteligente de escenas
    if segundos <= 30:
        num_escenas = 5
    elif segundos <= 45:
        num_escenas = 7
    elif segundos <= 60:
        num_escenas = 8
    elif segundos <= 90:
        num_escenas = 10
    else:
        num_escenas = 12

    palabras_por_escena_aprox = int(palabras_objetivo / num_escenas)

    # -------------------------------------------------
    # LÓGICA DE CANAL
    # -------------------------------------------------
    if canal.lower() == "deportes":
        reglas_canal = """
        ESTILO DEPORTIVO ANALÍTICO PROFESIONAL:

        - SOLO usar datos reales y verificables.
        - NO inventar estadísticas.
        - NO inventar récords.
        - Si no estás 100% seguro del dato, habla en términos generales sin números específicos.
        - Evitar fechas exactas si no se conocen con certeza.
        - No exagerar.
        - Tono de comentarista deportivo serio.
        - Enfocar en rendimiento, comparaciones históricas reales y contexto deportivo auténtico.
        - Prohibido crear jugadores, torneos o cifras falsas.
        """
    else:
        reglas_canal = """
        ESTILO MISTERIO / IMPACTO:

        - Tono intrigante o impactante.
        - Escalada progresiva.
        - No parecer artículo de Wikipedia.
        - Mantener tensión narrativa.
        """

    # -------------------------------------------------
    # MODO AGRESIVO
    # -------------------------------------------------
    if modo.lower() == "agresivo":
        reglas_tono = f"""
        MODO AGRESIVO ACTIVADO:

        OBJETIVO:
        Confrontar al espectador directamente.
        Generar incomodidad y fricción.

        REGLAS:

        - Usar segunda persona en varias escenas.
        - Cada escena debe empeorar la anterior.
        - Incluir consecuencias claras.
        - No usar signos de interrogación.
        - No usar metáforas poéticas.
        - No narración externa.
        - Final debe atacar identidad o forzar decisión directa.
        - Máximo {palabras_por_escena_aprox + 2} palabras por escena.
        """
    else:
        reglas_tono = f"""
        MODO NORMAL:

        - Tensión progresiva.
        - Narración fluida.
        - Mantener curiosidad.
        - Aproximadamente {palabras_por_escena_aprox} palabras por escena.
        """

    # -------------------------------------------------
    # PROMPT PRINCIPAL
    # -------------------------------------------------
    prompt_sistema = f"""
Eres un ARQUITECTO de retención viral para contenido vertical.

Tu objetivo:
- Maximizar retención.
- Mantener atención hasta el final.
- Incentivar comentarios.

Duración objetivo: {segundos} segundos.
Total aproximado de palabras: {palabras_objetivo}.
Número de escenas: {num_escenas}.
Promedio palabras por escena: {palabras_por_escena_aprox}.

{reglas_canal}
{reglas_tono}

ESTRUCTURA OBLIGATORIA:

1) Hook inmediato.
2) Desarrollo creciente.
3) Punto de mayor tensión.
4) Cierre fuerte.

Cada escena debe tener EXACTAMENTE:
- texto
- palabra_clave (una palabra potente, no repetir)
- prompt_imagen

REGLAS PARA prompt_imagen:

Debe incluir:
1. Tipo de plano
2. Ubicación concreta
3. Edad aproximada del personaje
4. Emoción visible
5. Acción específica
6. Hora del día
7. Ambiente o clima
8. Sensación cinematográfica realista

Debe ser:
- Generable por IA.
- Diferente entre escenas.
- No repetitivo.
- No genérico.

FORMATO JSON OBLIGATORIO:

{{
  "tipo_contenido": "{canal}",
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
            model="gpt-4o",
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": f"Tema: {tema}"}
            ],
            response_format={"type": "json_object"}
        )

        data = json.loads(response.choices[0].message.content)

        if "guion" not in data:
            raise ValueError("JSON sin guion")

        return data

    except Exception as e:
        print(f"❌ Error en GPT Engine: {e}")
        return None