import json
import sqlite3
import sys

from embed import Embedder

embedder = Embedder(device='cpu', instruction='Represent the mathematical document for retrieval')
# db_path = "file_contents.db"
db_path = "files_small.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT * FROM files")
rows = cursor.fetchall()
texts_to_embed = [row[1] for row in rows]
embedded_texts = embedder.embed(texts_to_embed)

cursor.execute("""
    CREATE TABLE embedded_files
    (path TEXT, embedding BLOB)
""")

for (path, _), embedding in zip(rows, embedded_texts):
    emb_str = json.dumps(embedding)
    cursor.execute("INSERT INTO embedded_files (path, embedded_content) VALUES (?, ?)", (path, emb_str))

conn.commit()
conn.close()
