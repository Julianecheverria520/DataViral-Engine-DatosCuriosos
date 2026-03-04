import sqlite3

conn = sqlite3.connect("mundial.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS prueba (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT
)
""")

conn.commit()
conn.close()

print("Base creada correctamente")