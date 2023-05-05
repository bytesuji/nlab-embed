import sqlite3

from embed import Embedder

embedder = Embedder()
conn = sqlite3.connect("file_contents.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM files")
rows = cursor.fetchall()
texts_to_embed = [row[1] for row in rows]
embedded_texts = embedder.embed(texts_to_embed)

cursor.execute("""
    CREATE TABLE embedded_files
    (path TEXT, embedded_content BLOB)
""")

for (path, _), embedded_text in zip(rows, embedded_texts):
    cursor.execute("INSERT INTO embedded_files (path, embedded_content) VALUES (?, ?)", (path, embedded_text))

conn.commit()
conn.close()
