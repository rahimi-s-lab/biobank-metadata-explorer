from flask import Flask, request, jsonify, send_from_directory

from rag import build_vector_index

app = Flask(__name__, static_folder='static')

# Initialized in the main block
index = None

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    k = request.args.get('k', default=3, type=int)  # Get 'k' from the request, default to 3 if not provided
    threshold = request.args.get('threshold', default=0.1, type=float)
    retriever = index.as_retriever(
            search_type="similarity_score_threshold", search_kwargs={"score_threshold": threshold, "k": k}  # Adjust threshold as needed (0-1)
        )
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400

    # Invoke the retriever with the query
    results = retriever.invoke(query)
    
    # Format the results
    formatted_results = [format(doc) for doc in results]
    
    return jsonify(formatted_results)


def format(doc):
    return doc.metadata
            

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--model', type=str, default='mxbai', help='Model to use for embeddings')
    parser.add_argument('--refresh', action='store_true', help='Refresh the vector index', default=False)
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Host to run the app on')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the app on')
    parser.add_argument('--limit', type=int, help='Limit the number of documents indexed', default=None)
    args = parser.parse_args()

    print(f"building index {args.refresh}")
    index = build_vector_index(model=args.model, refresh=args.refresh, limit=args.limit)

    app.run(debug=True, host=args.host, port=args.port)