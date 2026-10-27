from flask import Flask,request,jsonify
from flask_cors import CORS
from sentence_transformers import SentenceTransformer
from search_engine import (
    load_or_build_index,
    search,
    create_chunks,
    generate_embeddings
)
from pathlib import Path
from werkzeug.utils import secure_filename
import numpy as np
from pypdf import PdfReader
import pickle
from docx import Document

app=Flask(__name__)
CORS(app)

UPLOADED_INDEX_PATH = Path("uploaded_index.pkl")

uploaded_chunks = []
uploaded_embeddings = None

def save_uploaded_index():
    index_data = {
        "chunks": uploaded_chunks,
        "embeddings": uploaded_embeddings
    }

    with open(UPLOADED_INDEX_PATH, "wb") as file:
        pickle.dump(index_data, file)

def load_uploaded_index():
    global uploaded_chunks, uploaded_embeddings

    if not UPLOADED_INDEX_PATH.exists():
        return

    with open(UPLOADED_INDEX_PATH, "rb") as file:
        index_data = pickle.load(file)

    uploaded_chunks = index_data["chunks"]
    uploaded_embeddings = index_data["embeddings"]

def remove_uploaded_document(filename):
    global uploaded_chunks, uploaded_embeddings

    # Find the positions of chunks belonging to other files
    keep_indices = [
        i for i, chunk in enumerate(uploaded_chunks)
        if chunk["filename"] != filename
    ]

    # Keep only chunks that do not belong to this filename
    uploaded_chunks = [
        uploaded_chunks[i] for i in keep_indices
    ]

    # Keep the matching embedding rows in the same order
    if uploaded_embeddings is not None:
        uploaded_embeddings = uploaded_embeddings[keep_indices]

model = SentenceTransformer("all-MiniLM-L6-v2")
all_chunks, chunk_embeddings = load_or_build_index(
    model, "search_index.pkl"
)
load_uploaded_index()

@app.route("/search", methods=["POST"])
def search_route():
    data = request.get_json()
    query = data.get("query", "").strip()

    if not query:
        return jsonify({"error": "Please enter a question."}), 400

    search_chunks = all_chunks + uploaded_chunks

    print("\n--- DEBUG UPLOADED CHUNKS ---")

    for chunk in uploaded_chunks:
        if chunk["filename"] == "my_notes.txt":
            print(chunk["text"])

    print("--- END DEBUG ---\n")

    if uploaded_embeddings is not None:
        search_embeddings = np.concatenate(
            (chunk_embeddings, uploaded_embeddings), axis=0
        )
    else:
        search_embeddings = chunk_embeddings

    relevant_results = search(
        query,
        model,
        search_chunks,
        search_embeddings,
        threshold=0.15
    )

    results = []

    for pair in relevant_results[:3]:
        chunk = pair[0]
        score = float(pair[1])

        results.append({
            "title": chunk["filename"].replace(".txt", "").replace("_", " ").title(),
            "filename": chunk["filename"],
            "score": score,
            "text": chunk["text"]
        })

    return jsonify({
        "query": query,
        "results": results
    })

UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)

@app.route("/upload", methods=["POST"])
def upload_file():
    global uploaded_embeddings, uploaded_chunks
    if "file" not in request.files:
        return jsonify({"error": "No file was provided."}), 400

    file = request.files["file"]

    if not file.filename:
        return jsonify({"error": "Please select a file."}), 400

    if Path(file.filename).suffix.lower() not in [".txt",".pdf",".docx"]:
        return jsonify({"error": "Only TXT ,PDF and DOCX files are supported currently."}), 400

    filename = secure_filename(file.filename)

    if not filename:
        return jsonify({"error": "Invalid filename."}), 400

    save_path = UPLOAD_FOLDER / filename
    file.save(save_path)

    if save_path.suffix.lower() == ".txt":
        content = save_path.read_text(encoding="utf-8")

    elif save_path.suffix.lower() == ".pdf":
        reader = PdfReader(str(save_path))

        content = "\n\n".join(
            page.extract_text() or ""
            for page in reader.pages
        )
        if not content.strip():
            save_path.unlink(missing_ok=True)

            return jsonify({
                "error": "No selectable text found. Scanned PDFs require OCR."
            }), 400

    elif save_path.suffix.lower() == ".docx":
        doc = Document(str(save_path))

        content = "\n\n".join(
            paragraph.text
            for paragraph in doc.paragraphs
            if paragraph.text.strip()
        )

    else:
        return jsonify({"error": "Only TXT and PDF files are supported."}), 400

    file_data = [{
        "filename": filename,
        "content": content
    }]

    new_chunks = create_chunks(file_data)

    if not new_chunks:
        save_path.unlink()
        return jsonify({"error": "The file contains no searchable text."}), 400

    new_embeddings = generate_embeddings(new_chunks, model)

    remove_uploaded_document(filename)

    print("Remaining chunks for this file:",
      [chunk["text"] for chunk in uploaded_chunks
       if chunk["filename"] == filename])

    uploaded_chunks.extend(new_chunks)

    if uploaded_embeddings is None:
        uploaded_embeddings = new_embeddings
    else:
        uploaded_embeddings = np.concatenate(
            (uploaded_embeddings, new_embeddings), axis=0
        )

    save_uploaded_index()

    return jsonify({
        "message": f"{filename} uploaded successfully."
    }), 200

@app.route("/delete/<filename>", methods=["DELETE"])
def delete_uploaded_file(filename):
    global uploaded_chunks, uploaded_embeddings

    # Find the uploaded file safely
    filename = secure_filename(filename)

    if not filename:
        return jsonify({"error": "Invalid filename."}), 400

    file_path = UPLOAD_FOLDER / filename

    # Only allow deletion of an existing uploaded file
    if not file_path.is_file():
        return jsonify({"error": "Uploaded document not found."}), 404

    # Remove its chunks and matching embeddings
    remove_uploaded_document(filename)

    # Save the updated index
    save_uploaded_index()

    # Remove the physical file
    file_path.unlink(missing_ok=True)

    return jsonify({
        "message": f"{filename} deleted successfully."
    }), 200

@app.route("/documents", methods=["GET"])
def list_uploaded_documents():
    documents = []

    for filename in sorted({
        chunk["filename"] for chunk in uploaded_chunks
    }):
        documents.append({
            "filename": filename
        })

    return jsonify({"documents": documents}), 200

if __name__=="__main__":
    app.run(debug=True)