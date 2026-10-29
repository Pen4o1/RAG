import os
from pathlib import Path
from dotenv import load_dotenv
from fastembed import TextEmbedding
from pinecone import Pinecone, ServerlessSpec

from markdown_blocks import chunk_markdown

load_dotenv()

INDEX_NAME = "rag-index"
EMBEDDING_DIM = 384  # all-MiniLM-L6-v2 produces 384-dimensional vectors
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
CACHE_DIR = Path(__file__).resolve().parent / ".cache" / "fastembed"

# 1. Initialize local embedding model & Pinecone client
model = TextEmbedding(
    MODEL_NAME,
    cache_dir=str(CACHE_DIR),
    threads=1,
    providers=["CPUExecutionProvider"],
)
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# 2. Create index if it doesn't exist yet
existing_indexes = [idx.name for idx in pc.list_indexes()]
if INDEX_NAME not in existing_indexes:
    print(f"Creating Pinecone index '{INDEX_NAME}'...")
    pc.create_index(
        name=INDEX_NAME,
        dimension=EMBEDDING_DIM,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

index = pc.Index(INDEX_NAME)

def load_documents(data_dir="./data"):
    docs = []
    path = Path(data_dir)
    for file_path in path.glob("*.*"):
        if file_path.suffix in [".txt", ".md"]:
            with open(file_path, "r", encoding="utf-8") as f:
                docs.append({"content": f.read(), "source": file_path.name})
    return docs

def main():
    print("Loading documents from ./data...")
    documents = load_documents()
    
    if not documents:
        print("No documents found in ./data!")
        return

    vectors_to_upsert = []
    global_id = 0

    for doc in documents:
        chunks = chunk_markdown(doc["content"])
        print(f"Embedding {len(chunks)} chunk(s) from {doc['source']}...")
        embeddings = list(model.embed(chunk["text"] for chunk in chunks))

        for idx, (chunk, emb) in enumerate(zip(chunks, embeddings)):
            vectors_to_upsert.append({
                "id": f"vec_{global_id}",
                "values": emb.tolist(),
                "metadata": {
                    "text": chunk["text"],
                    "source": doc["source"],
                    "chunk_index": idx,
                    "kind": chunk["kind"],
                }
            })
            global_id += 1

    print(f"Replacing the index with {len(vectors_to_upsert)} vectors...")
    index.delete(delete_all=True)
    for start in range(0, len(vectors_to_upsert), 100):
        index.upsert(vectors=vectors_to_upsert[start:start + 100])
    print("Pinecone vector database successfully populated!")

if __name__ == "__main__":
    main()