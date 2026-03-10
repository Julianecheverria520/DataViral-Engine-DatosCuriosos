import edge_tts
import asyncio
import json
import os
from moviepy.editor import AudioFileClip
from .limpieza_engine import limpiar_texto_para_tts, corregir_json_subtitulos

VOZ_POR_DEFECTO = "es-MX-JorgeNeural"

async def proceso_voz_async(texto_fonetico, audio_path, timestamps_path, velocidad):
    """Bucle interno para manejar la comunicación con el servidor."""
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
    return word_boundaries

def generar_voz(texto_original, output_audio_path, output_timestamps_path, velocidad="+6%"):
    print(f"🎙️ Generando Voz para: {os.path.basename(output_audio_path)}")
    
    # 1. Preparación fonética
    texto_fonetico = limpiar_texto_para_tts(texto_original)

    # 2. Ejecución Asíncrona con manejo de errores
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    word_boundaries = loop.run_until_complete(
        proceso_voz_async(texto_fonetico, output_audio_path, output_timestamps_path, velocidad)
    )

    # 3. PLAN B: Si el servidor no envió timestamps, los creamos manualmente
    if not word_boundaries:
        print("⚠️ Advertencia: Servidor sin datos de tiempo. Aplicando estimación...")
        if os.path.exists(output_audio_path):
            audio = AudioFileClip(output_audio_path)
            duracion_total = audio.duration
            audio.close()
            
            palabras = texto_fonetico.split()
            t_por_p = duracion_total / len(palabras)
            for i, p in enumerate(palabras):
                word_boundaries.append({
                    "palabra": p,
                    "inicio": i * t_por_p,
                    "fin": (i + 1) * t_por_p
                })

    # 4. CORRECCIÓN ORTOGRÁFICA (Revertimos fonética a original)
    final_boundaries = corregir_json_subtitulos(word_boundaries)

    # 5. ESCRITURA FORZADA AL DISCO
    try:
        with open(output_timestamps_path, "w", encoding="utf-8") as f:
            json.dump(final_boundaries, f, indent=4, ensure_ascii=False)
        print(f"✅ Timestamps generados exitosamente en: {output_timestamps_path}")
        return True
    except Exception as e:
        print(f"❌ Error fatal al escribir el JSON: {e}")
        return False