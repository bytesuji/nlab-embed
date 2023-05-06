import json
import sqlite3
import sys
import hnswlib

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

    # Create an hnswlib index and add the embeddings
    dim = len(embedded_texts[0])
    num_elements = len(embedded_texts)
    p = hnswlib.Index(space='cosine', dim=dim)
    p.init_index(max_elements=num_elements, ef_construction=100, M=16)

    for i, embedding in enumerate(embedded_texts):
        p.add_items([embedding], [i])

    # Save the hnswlib index
    p.save_index("nlab_vectors.idx")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS embedded_file_ids
        (path TEXT, embedding_id INTEGER)
    """)

    for (path, _), i in zip(rows, range(len(embedded_texts))):
        cursor.execute("INSERT INTO embedded_file_ids (path, embedding_id) VALUES (?, ?)", (path, i))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()
