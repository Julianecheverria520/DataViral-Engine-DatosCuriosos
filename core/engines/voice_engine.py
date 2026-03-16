import edge_tts
import asyncio
import json
import os
from moviepy.editor import AudioFileClip
from core.config.limpieza_engine import limpiar_texto_para_tts, corregir_json_subtitulos

VOZ_POR_DEFECTO = "es-MX-JorgeNeural"

async def proceso_voz_async(texto_fonetico, audio_path, velocidad):
    """Bucle con captura forzada de boundaries."""
    communicate = edge_tts.Communicate(texto_fonetico, VOZ_POR_DEFECTO, rate=velocidad)
    word_boundaries = []
    
    with open(audio_path, "wb") as fp:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                fp.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                palabra = chunk["text"].strip()
                inicio = chunk["offset"] / 10000000
                duracion = chunk["duration"] / 10000000
                if palabra:
                    word_boundaries.append({
                        "palabra": palabra, 
                        "inicio": inicio,
                        "fin": inicio + duracion
                    })
    
    await asyncio.sleep(0.5)
    return word_boundaries

def _estimar_tiempos_mejorado(texto_fonetico, duracion_total):
    """
    Estimación mejorada cuando edge_tts no devuelve boundaries.
    Asigna pesos basados en longitud y signos de puntuación.
    """
    palabras = texto_fonetico.split()
    if not palabras:
        return []
    
    pesos = []
    for i, p in enumerate(palabras):
        peso = len(p)
        if p.endswith(('.', ',', ';', ':', '!', '?')):
            peso += 3
        elif p.endswith(('-', '—', ')', ']', '}')):
            peso += 1
        if i == 0 or i == len(palabras)-1:
            peso = int(peso * 1.1)
        pesos.append(peso)
    
    total_peso = sum(pesos)
    word_boundaries = []
    tiempo_actual = 0.0
    
    for i, p in enumerate(palabras):
        duracion = (pesos[i] / total_peso) * duracion_total
        word_boundaries.append({
            "palabra": p,
            "inicio": tiempo_actual,
            "fin": tiempo_actual + duracion
        })
        tiempo_actual += duracion
    
    if word_boundaries and abs(word_boundaries[-1]["fin"] - duracion_total) > 0.001:
        word_boundaries[-1]["fin"] = duracion_total
    
    return word_boundaries

def generar_voz(texto_original, output_audio_path, output_timestamps_path, velocidad="+10%"):
    print(f"🎙️ Generando Voz Real para: {os.path.basename(output_audio_path)}")
    
    texto_fonetico = limpiar_texto_para_tts(texto_original)

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    word_boundaries = loop.run_until_complete(
        proceso_voz_async(texto_fonetico, output_audio_path, velocidad)
    )

    if not word_boundaries:
        print("❌ ERROR: El servidor no envió tiempos. Usando estimación mejorada basada en audio...")
        if os.path.exists(output_audio_path):
            audio = AudioFileClip(output_audio_path)
            duracion_total = audio.duration
            audio.close()
            word_boundaries = _estimar_tiempos_mejorado(texto_fonetico, duracion_total)
            print(f"   ✅ Estimación mejorada completada: {len(word_boundaries)} palabras generadas.")
        else:
            print("   ❌ No se encontró el archivo de audio, no se pueden generar timestamps.")
            return False

    if word_boundaries:
        final_boundaries = corregir_json_subtitulos(word_boundaries)
    else:
        final_boundaries = []

    with open(output_timestamps_path, "w", encoding="utf-8") as f:
        json.dump(final_boundaries, f, indent=4, ensure_ascii=False)
    
    print(f"✅ Proceso terminado. Timestamps: {len(final_boundaries)} palabras.")
    return True