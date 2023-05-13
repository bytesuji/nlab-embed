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
    data = request.get_json(force=True)
    query = data['query']
    page = data.get('page', 0)
    results_per_page = 15

    # Embed the user's query
    query_embedding = embedder.embed([query])[0]

    # Find the top matches
    total_results = 100  # You can adjust this number based on your desired total results
    new_total_results = data.get('new_total_results', None)
    if new_total_results:
        total_results = int(new_total_results)
    top_indices, _ = p.knn_query([query_embedding], k=total_results)

    # Paginate the results
    start_index = page * results_per_page
    end_index = start_index + results_per_page
    paginated_indices = top_indices[0][start_index:end_index]

    result_paths = [get_path(index) for index in paginated_indices]
    return jsonify(result_paths)

if __name__ == '__main__':
    app.run(port=8080)
