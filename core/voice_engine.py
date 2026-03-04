import edge_tts
import asyncio
import json
from moviepy.editor import AudioFileClip

VOZ_POR_DEFECTO = "es-MX-JorgeNeural"


def generar_voz(texto, output_audio_path, output_timestamps_path):

    async def comunicado():

        communicate = edge_tts.Communicate(
            texto,
            VOZ_POR_DEFECTO,
            rate="+12%"
        )

        word_boundaries = []

        print("🎙️ Generando voz...")

        try:
            with open(output_audio_path, "wb") as fp:
                async for chunk in communicate.stream():

                    if chunk["type"] == "audio":
                        fp.write(chunk["data"])

                    elif chunk["type"] == "WordBoundary":

                        inicio = chunk["offset"] / 10000000
                        duracion = chunk["duration"] / 10000000

                        if duracion <= 0.02:
                            continue

                        word_boundaries.append({
                            "palabra": chunk["text"].strip(),
                            "inicio": inicio,
                            "fin": inicio + duracion
                        })

            # ==========================================
            # 🔎 VALIDACIÓN
            # ==========================================

            audio = AudioFileClip(output_audio_path)
            duracion_total = audio.duration
            audio.close()

            # 🔥 Si no llegaron timestamps → fallback automático
            if not word_boundaries:
                print("⚠️ No se recibieron WordBoundaries.")
                print("🔁 Generando timestamps proporcionales...")

                palabras = texto.split()
                total_palabras = len(palabras)

                if total_palabras == 0:
                    raise Exception("Texto vacío.")

                tiempo_por_palabra = duracion_total / total_palabras

                tiempo_actual = 0

                for palabra in palabras:
                    inicio = tiempo_actual
                    fin = inicio + tiempo_por_palabra

                    word_boundaries.append({
                        "palabra": palabra,
                        "inicio": inicio,
                        "fin": fin
                    })

                    tiempo_actual = fin

            # ==========================================
            # 🔧 AJUSTE FINAL CONTRA DURACIÓN REAL
            # ==========================================

            ultimo_timestamp = word_boundaries[-1]["fin"]
            diferencia = duracion_total - ultimo_timestamp

            if abs(diferencia) > 0.05:
                print("⚙️ Ajustando sincronización global...")
                for w in word_boundaries:
                    w["inicio"] += diferencia
                    w["fin"] += diferencia

            with open(output_timestamps_path, "w", encoding="utf-8") as f:
                json.dump(word_boundaries, f, indent=4, ensure_ascii=False)

            print(f"✅ Audio y timestamps generados ({len(word_boundaries)} palabras)")
            return True

        except Exception as e:
            print(f"❌ Error en voice_engine: {e}")
            return False

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    resultado = loop.run_until_complete(comunicado())
    loop.close()
    return resultado