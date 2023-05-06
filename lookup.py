import json
import sqlite3
import hnswlib

from embed import Embedder

def main():
    db_path = "files_full2.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Load hnswlib index
    p = hnswlib.Index(space='cosine', dim=768)  # Set the dim to the dimension of your embeddings
    p.load_index("nlab_vectors.idx")

    # Get file paths from the database
    cursor.execute("SELECT * FROM embedded_file_ids")
    rows = cursor.fetchall()
    paths = [row[0] for row in rows]

    # Instantiate an embedder
    embedder = Embedder(instruction='Represent the mathematical user query for retrieving supporting documents; Input:')

    while True:
        query = input("Enter your query (or type 'exit' to quit): ")

        if query.lower() == 'exit':
            break

        # Embed the user's query
        query_embedding = embedder.embed([query])[0]

        # Find the top 15 matches
        top_indices, _ = p.knn_query([query_embedding], k=15)

        print("Top 15 matching file paths:")
        for index in top_indices[0]:
            print(paths[int(index)])

    conn.close()

if __name__ == "__main__":
    main()
