from flask import Flask, request, jsonify, render_template
import json
import sqlite3
import hnswlib
from embed import Embedder

app = Flask(__name__)

db_path = "files_full2.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Load hnswlib index
p = hnswlib.Index(space='cosine', dim=768)
p.load_index("nlab_vectors.idx")

# Get file paths from the database
cursor.execute("SELECT * FROM embedded_file_ids")
rows = cursor.fetchall()
paths = [row[0] for row in rows]

# Instantiate an embedder
embedder = Embedder(instruction='Represent the mathematical user query for retrieving supporting documents; Input:')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']

    # Embed the user's query
    query_embedding = embedder.embed([query])[0]

    # Find the top 15 matches
    top_indices, _ = p.knn_query([query_embedding], k=15)

    result_paths = [paths[int(index)] for index in top_indices[0]]
    return jsonify(result_paths)

if __name__ == '__main__':
    app.run(debug=True)
