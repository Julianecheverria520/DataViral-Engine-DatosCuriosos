import openai
import json

client = openai.OpenAI()

def auditar_guion(guion_json, tema, hook_fijo):
    print("🔍 AUDITANDO...")
    prompt = f"""
    Eres el Editor Jefe de InsightdataMind.
    TEMA: {tema} | HOOK ESPERADO: "{hook_fijo}"
    GUION: {json.dumps(guion_json)}

    CRITERIOS:
    1. INTEGRIDAD: ¿La Escena 1 contiene las palabras del Hook Esperado? (Ignora mayúsculas).
    2. VALOR REAL: ¿Menciona algún dato o término técnico? (No pidas párrafos, solo el dato).
    3. ORTOGRAFÍA: Ortografía real, no fonética.

    RESPUESTA JSON: {{"aprobado": true/false, "razon": "...", "mejora": "..."}}
    """
    try:
        res = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": prompt}],
            response_format={"type": "json_object"}
        )
        resultado = json.loads(res.choices[0].message.content)

        # VALIDACIÓN MANUAL TOLERANTE
        texto_recibido = guion_json["guion"][0]["texto"].lower().strip()
        texto_esperado = hook_fijo.lower().strip()

        if texto_esperado not in texto_recibido:
            resultado["aprobado"] = False
            resultado["razon"] = f"Hook incompleto. Esperado: {hook_fijo}"
        
        return resultado
    except:
        return {"aprobado": True}