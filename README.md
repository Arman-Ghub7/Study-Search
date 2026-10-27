# StudySearch — Semantic Search Engine

StudySearch is a semantic search application that helps students find relevant information in their study notes and educational documents using natural-language queries.

## Features

- Semantic search using Sentence Transformers and cosine similarity
- Upload TXT, PDF, and DOCX documents
- Extract text and split documents into searchable chunks
- Generate embeddings for uploaded content
- Persist uploaded chunks and embeddings across server restarts
- Replace existing uploaded documents
- View and delete uploaded documents
- Evaluate retrieval quality using Precision@3, Recall@3, MRR, and threshold comparisons

## Tech Stack

**Backend:** Python, Flask, Flask-CORS

**Machine Learning:** Sentence Transformers (`all-MiniLM-L6-v2`), NumPy, scikit-learn

**Document Processing:** pypdf, python-docx

**Frontend:** HTML, CSS, JavaScript

## Project Structure

```text
semantic-search/
├── documents/          # Sample study notes
├── Web_interface/      # Frontend
├── app.py              # Flask API
├── search_engine.py    # Chunking, embeddings, and search
├── evaluation.py       # Retrieval evaluation
├── main.py              # Search engine entry point
├── requirements.txt
├── README.md
└── .gitignore
```

## Getting Started

### 1. Clone the repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd semantic-search
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Start the backend

```bash
python app.py
```

### 5. Open the frontend

Open `Web_interface/index.html` using VS Code Live Server.

The frontend communicates with the Flask API running locally at `http://127.0.0.1:5000`.

The original search index may need to be generated from the sample documents when running the project for the first time.

## Evaluation

The current 10-query evaluation set produced:

| Metric | Result |
|---|---:|
| Top-1 test accuracy | 100% |
| Mean Precision@3 | 0.7083 |
| Mean Recall@3 | 1.0000 |
| Mean Reciprocal Rank | 1.0000 |

On this test set, thresholds of 0.10, 0.15, and 0.20 each achieved 100% under the current pass/fail rule.

These results are preliminary because the test set is small and relevance is labeled at the file level. They should not be interpreted as guaranteed real-world accuracy.

## Limitations

- Scanned PDFs require OCR, which is not currently implemented.
- DOCX extraction currently focuses on paragraphs.
- Uploaded document storage is designed for a local, single-user prototype.
- The frontend expects the backend to run locally.

## Future Improvements

- Better retrieval evaluation with passage-level relevance labels
- Search filters and highlighted matching passages
- OCR for scanned PDFs
- Improved document management and storage
- Deployment for remote access

## License

Add a license if you intend to distribute or reuse this project publicly.
