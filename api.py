import hnswlib
import json
import sqlite3

from embed import Embedder
from flask import Flask, request, jsonify, render_template

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

def get_path(index):
    i = int(index)
    raw_path = paths[i]
    return raw_path.replace('/Users/albert/Downloads/', 'https://')

# Instantiate an embedder
embedder = Embedder(device='cpu', instruction='Represent the mathematical query for retrieving supporting documents; Input:')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.get_json(force=True)['query']

    # Embed the user's query
    query_embedding = embedder.embed([query])[0]

    # Find the top 15 matches
    top_indices, _ = p.knn_query([query_embedding], k=15)

    result_paths = [get_path(index) for index in top_indices[0]]
    return jsonify(result_paths)

if __name__ == '__main__':
    app.run(port=8080)
