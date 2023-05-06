import json
import sqlite3
from embed import Embedder
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def knn(embedding, all_embeddings, paths, k=5):
    similarities = cosine_similarity([embedding], all_embeddings)
    indices = np.argsort(-similarities[0])[:k]  # Get indices of top k similarities
    top_k_paths = [paths[i] for i in indices]
    return top_k_paths

def main():
    db_path = "files_full.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM embedded_files")
    rows = cursor.fetchall()
    paths = [row[0] for row in rows]
    embeddings = [json.loads(row[1]) for row in rows]
    
    # Instantiate an embedder
    embedder = Embedder(instruction='Represent the mathematical user query for retrieving supporting documents; Input:')

    while True:
        query = input("Enter your query (or type 'exit' to quit): ")

        if query.lower() == 'exit':
            break

        # Embed the user's query
        query_embedding = embedder.embed([query])[0]

        # Find the top 5 matches
        top_paths = knn(query_embedding, embeddings, paths, k=5)

        print("Top 5 matching file paths:")
        for path in top_paths:
            print(path)

    conn.close()

if __name__ == "__main__":
    main()
