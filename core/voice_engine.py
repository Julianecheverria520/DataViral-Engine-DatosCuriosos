import edge_tts
import asyncio
import json
import os
from moviepy.editor import AudioFileClip

VOZ_POR_DEFECTO = "es-MX-JorgeNeural" 

def generar_voz(texto, output_audio_path, output_timestamps_path):
    async def comunicado():
        communicate = edge_tts.Communicate(texto, VOZ_POR_DEFECTO)
        word_boundaries = []
        
        print(f"🎙️ Conectando con el servidor de voz...")
        
        try:
            # 1. Descargar el audio
            with open(output_audio_path, "wb") as fp:
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        fp.write(chunk["data"])
                    elif chunk["type"] == "WordBoundary":
                        word_boundaries.append({
                            "palabra": chunk["text"],
                            "inicio": chunk["offset"] / 10000000,
                            "duracion": chunk["duration"] / 10000000
                        })
            
            # 2. Modo Respaldo Matemático (Si fallan los timestamps del servidor)
            if not word_boundaries:
                print("⚠️ Servidor no envió tiempos. Calculando distribución proporcional...")
                
                # Cargamos el audio recién creado para saber su duración real
                audio_temp = AudioFileClip(output_audio_path)
                duracion_total = audio_temp.duration
                audio_temp.close()

                palabras = texto.split()
                tiempo_por_palabra = duracion_total / len(palabras)
                
                for i, p in enumerate(palabras):
                    word_boundaries.append({
                        "palabra": p,
                        "inicio": i * tiempo_por_palabra,
                        "duracion": tiempo_por_palabra
                    })

            print(f"📥 Audio listo ({len(word_boundaries)} palabras).")

            # 3. Guardar JSON de timestamps
            timestamps = []
            for word in word_boundaries:
                timestamps.append({
                    "palabra": word["palabra"],
                    "inicio": word["inicio"],
                    "fin": word["inicio"] + word["duracion"],
                    "duracion": word["duracion"]
                })

            with open(output_timestamps_path, "w", encoding="utf-8") as f:
                json.dump(timestamps, f, indent=4, ensure_ascii=False)
            
            return True

        except Exception as e:
            print(f"❌ Error interno: {e}")
            return False

    try:
        # Ejecución estable en Windows
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        resultado = loop.run_until_complete(comunicado())
        loop.close()
        return resultado
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        return False