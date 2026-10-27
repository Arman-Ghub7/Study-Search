from sentence_transformers import SentenceTransformer
from search_engine import load_or_build_index,search

test_cases = [
    {
        "query": "What is conditional probability?",
        "expected_topic": "probability",
        "relevant_files": ["probability.txt"]
    },
    {
        "query": "What is the F1-score used for?",
        "expected_topic": "machine_learning",
        "relevant_files": ["machine_learning.txt"]
    },
    {
        "query": "How likely is an event to happen?",
        "expected_topic": "probability",
        "relevant_files": ["probability.txt"]
    },
    {
        "query": "What does the average tell us about a dataset?",
        "expected_topic": "statistics",
        "relevant_files": ["statistics.txt"]
    },
    {
        "query": "How can I tell if my spam detector misses actual spam?",
        "expected_topic": "machine_learning",
        "relevant_files": ["machine_learning.txt"]
    },
    {
        "query": "How does a model learn useful patterns from examples?",
        "expected_topic": "machine_learning",
        "relevant_files": ["machine_learning.txt"]
    },
    {
        "query": "How do I summarize a collection of numbers using one value?",
        "expected_topic": "statistics",
        "relevant_files": ["statistics.txt"]
    },
    {
        "query": "How can I measure uncertainty about an outcome?",
        "expected_topic": "probability",
        "relevant_files": ["probability.txt"]
    },
    {
        "query": "How do I bake a chocolate cake?",
        "expected_topic": "irrelevant",
        "relevant_files": []
    },
    {
        "query": "How do I repair a bicycle chain?",
        "expected_topic": "irrelevant",
        "relevant_files": []
    }
]


model = SentenceTransformer("all-MiniLM-L6-v2")
all_chunks,chunk_embeddings=load_or_build_index(model,"search_index.pkl")


def precision_at_k(results, relevant_files, k=3):
    top_results = results[:k]

    if not top_results:
        return 0.0

    relevant_count = sum(
        1 for chunk, score in top_results
        if chunk["filename"] in relevant_files
    )

    return relevant_count / k



def recall_at_k(results, relevant_files, k=3):
    if not relevant_files:
        return None

    top_results = results[:k]

    retrieved_relevant_files = {
        chunk["filename"]
        for chunk, score in top_results
        if chunk["filename"] in relevant_files
    }

    return len(retrieved_relevant_files) / len(relevant_files)



def reciprocal_rank(results, relevant_files):
    for rank, (chunk, score) in enumerate(results, start=1):
        if chunk["filename"] in relevant_files:
            return 1 / rank

    return 0.0



total_passes = 0
precision_scores = []
recall_scores = []
reciprocal_ranks = []

K = 3

for case in test_cases:
    query = case["query"]
    relevant_files = case["relevant_files"]

    relevant_results = search(
        query,
        model,
        all_chunks,
        chunk_embeddings,
        threshold=0.15
    )

    # Check whether the expected behavior occurred
    if not relevant_files:
        passed = len(relevant_results) == 0
    else:
        passed = (
            bool(relevant_results)
            and relevant_results[0][0]["filename"]
            in relevant_files
        )

    if passed:
        total_passes += 1

    # Evaluate ranking quality for relevant queries
    if relevant_files:
        precision_scores.append(
            precision_at_k(relevant_results, relevant_files, K)
        )

        recall_scores.append(
            recall_at_k(relevant_results, relevant_files, K)
        )

        reciprocal_ranks.append(
            reciprocal_rank(relevant_results, relevant_files)
        )

    for chunk, score in relevant_results[:K]:
        print(f"  {chunk['filename']} | similarity: {score:.4f}")

print("\n===== EVALUATION SUMMARY =====")
print(f"Top-1 test accuracy: {total_passes / len(test_cases) * 100:.2f}%")
print(f"Mean Precision@{K}: {sum(precision_scores) / len(precision_scores):.4f}")
print(f"Mean Recall@{K}: {sum(recall_scores) / len(recall_scores):.4f}")
print(f"Mean Reciprocal Rank: {sum(reciprocal_ranks) / len(reciprocal_ranks):.4f}")



print("\n===== THRESHOLD COMPARISON =====")

for threshold in [0.10, 0.15, 0.20, 0.25, 0.30]:
    passed = 0

    for case in test_cases:
        results = search(
            case["query"],
            model,
            all_chunks,
            chunk_embeddings,
            threshold=threshold
        )

        relevant_files = case["relevant_files"]

        if not relevant_files:
            correct = len(results) == 0
        else:
            correct = (
                bool(results)
                and results[0][0]["filename"] in relevant_files
            )

        if correct:
            passed += 1

    accuracy = passed / len(test_cases) * 100

    print(
        f"Threshold: {threshold:.2f} | "
        f"Top-1 test accuracy: {accuracy:.2f}%"
    )

