import pandas as pd
import os
import random

def sugerir_proximo_tema():
    path_csv = "output/metricas_rendimiento.csv"
    
    if not os.path.exists(path_csv):
        return "Comparación extrema de dinero entre empresas y países"

    try:
        df = pd.read_csv(path_csv)

        # Convertir columnas clave
        df['likes_totales'] = pd.to_numeric(df.get('likes_totales', 0), errors='coerce').fillna(0)
        df['vistas'] = pd.to_numeric(df.get('vistas', 0), errors='coerce').fillna(0)
        df['retencion_50'] = pd.to_numeric(df.get('retencion_50', 0), errors='coerce').fillna(0)
        df['comentarios'] = pd.to_numeric(df.get('comentarios', 0), errors='coerce').fillna(0)

        ultimo = df.iloc[-1]

        print("📊 Último video:")
        print(ultimo)

        if ultimo['vistas'] > 1000:
            return "Otra comparación extrema de dinero con diferente empresa"

        if ultimo['retencion_50'] > 25:
            return "Misma estructura pero con otra empresa tecnológica"

        if ultimo['comentarios'] > (ultimo['likes_totales'] * 0.2):
            return "Comparación polémica entre empresa y país"

        alternativas = [
            "Cuánto gana una empresa en 1 minuto vs salario promedio",
            "Empresas que podrían comprar países",
            "Objetos que cuestan más que un Ferrari",
            "Comparación de riqueza entre CEOs y países pequeños"
        ]

        return random.choice(alternativas)

    except Exception as e:
        print(f"⚠️ Error analizando datos: {e}")
        return "Comparación extrema de riqueza corporativa"