from sentence_transformers import SentenceTransformer
from search_engine import load_or_build_index,search

model = SentenceTransformer("all-MiniLM-L6-v2")
all_chunks,chunk_embeddings=load_or_build_index(model,"search_index.pkl")

query=input("Enter your query:")
relevant_results=search(query,model,all_chunks,chunk_embeddings,threshold=0.15)
if not relevant_results:
    print("No relevant result found.")
else:
    print("Search results:")
    for pair in relevant_results[:3]:
        print(f"{pair[0]["filename"]}")
        print(f"Similarity score: {pair[1]:.4f}")
        print(f"Answer: {pair[0]["text"]}")
