from pathlib import Path
import joblib
from sklearn.metrics.pairwise import cosine_similarity

def load_documents(folder_path):
    p=Path(folder_path)
    filesList=[]
    for item in p.iterdir():
        if item.is_file() and item.suffix==".txt":
            fileDict={}
            fileDict["filename"]=item.name
            fileDict["content"]=item.read_text(encoding="utf-8")
            filesList.append(fileDict)
    return filesList

def get_file_info(folder_path):
    folder=Path(folder_path)
    file_info={}

    for file in folder.glob("*.txt"):
        file_info[file.name]=file.stat().st_mtime
    return file_info

def create_chunks(filesList):
    all_chunks=[]
    for file in filesList:
        text=file["content"]
        chunks=text.strip().split("\n\n")
        for chunk in chunks:
            if chunk.strip():
                chunkDict={}
                chunkDict["filename"]=file["filename"]
                chunkDict["text"]=chunk.strip()
                all_chunks.append(chunkDict)
    return all_chunks

def generate_embeddings(all_chunks,model):
    chunk_texts=[chunk["text"] for chunk in all_chunks]
    chunk_embeddings=model.encode(chunk_texts)
    return chunk_embeddings

def load_or_build_index(model,index_path):
    file_info=get_file_info("documents")
    index_path=Path(index_path)

    index_is_valid=False
    if index_path.exists():
        loaded_index=joblib.load(index_path)
        if loaded_index["file_info"]==file_info:
            index_is_valid=True

    if index_is_valid:
        all_chunks=loaded_index["chunks"]
        chunk_embeddings=loaded_index["embeddings"]
    else:
        filesList=load_documents("documents")
        all_chunks=create_chunks(filesList)
        chunk_embeddings=generate_embeddings(all_chunks,model)
        
        search_index={
            "chunks":all_chunks,
            "embeddings":chunk_embeddings,
            "file_info":file_info
        }
        joblib.dump(search_index,index_path)
    return all_chunks,chunk_embeddings

def search(query,model,all_chunks,chunk_embeddings,threshold=0.15):
    query_embedding=model.encode([query])
    scores=cosine_similarity(query_embedding,chunk_embeddings)

    pairs= list(zip(all_chunks,scores[0]))
    ranked_results=sorted(pairs,key=lambda pair:pair[1],reverse=True)

    relevant_results=[item for item in ranked_results 
                    if item[1]>=threshold]
    return relevant_results