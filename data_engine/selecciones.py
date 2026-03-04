from data_engine.db import get_connection

def crear_tabla():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS selecciones (
        id INTEGER PRIMARY KEY,
        nombre TEXT,
        confederacion TEXT,
        clasificada INTEGER,
        partidos INTEGER,
        victorias INTEGER,
        empates INTEGER,
        derrotas INTEGER,
        goles_favor INTEGER,
        goles_contra INTEGER
    )
    """)

    conn.commit()
    conn.close()