import json
import sqlite3
import sys

from embed import Embedder
from multiprocessing import Process, Queue

def embed_process(texts, index, queue):
    device = f'cuda:{index}'
    embedder = Embedder(instruction='Represent the mathematical document for retrieval; Input:', device=device)

    embedded_texts = embedder.embed(texts)
    queue.put((index, embedded_texts))

def main():
    # db_path = "files_small.db"
    db_path = "files_full2.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM files")
    rows = cursor.fetchall()
    texts_to_embed = [row[1] for row in rows]

    # Split texts into 8 arrays
    split_texts = [texts_to_embed[i::8] for i in range(8)]

    # Launch 8 processes
    processes = []
    queue = Queue()
    for i in range(8):
        p = Process(target=embed_process, args=(split_texts[i], i, queue))
        processes.append(p)
        p.start()

    # Collect results
    all_embeddings = [None] * 8
    for _ in range(8):
        index, embedded_texts = queue.get()
        all_embeddings[index] = embedded_texts

    # Flatten the list of embeddings
    embedded_texts = [emb for sublist in zip(*all_embeddings) for emb in sublist]

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS embedded_files
        (path TEXT, embedding BLOB)
    """)

    for (path, _), embedding in zip(rows, embedded_texts):
        emb_str = json.dumps(embedding)
        cursor.execute("INSERT INTO embedded_files (path, embedding) VALUES (?, ?)", (path, emb_str))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()
