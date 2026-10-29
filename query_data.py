import os
from pathlib import Path

from dotenv import load_dotenv
from fastembed import TextEmbedding
from google import genai
from pinecone import Pinecone
from tenacity import retry, stop_after_attempt, wait_exponential

from markdown_blocks import parse_tables

load_dotenv()

INDEX_NAME = "rag-index"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
CACHE_DIR = Path(__file__).resolve().parent / ".cache" / "fastembed"

# Initialize services
client = genai.Client()
model = TextEmbedding(
    MODEL_NAME,
    cache_dir=str(CACHE_DIR),
    threads=1,
    providers=["CPUExecutionProvider"],
)
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(INDEX_NAME)

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
def generate_response_with_retry(prompt: str):
    return client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

def query_rag(query_text: str, top_k: int = 5) -> dict:
    # 1. Embed query vector locally
    query_vector = next(model.embed([query_text])).tolist()

    # 2. Query Pinecone Cloud index
    results = index.query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=True
    )

    matches = []
    for match in results["matches"]:
        metadata = match.get("metadata") or {}
        text = metadata.get("text", "")
        tables = parse_tables(text)
        matches.append({
            "text": text,
            "source": metadata.get("source", ""),
            "score": match.get("score"),
            "chunk_index": metadata.get("chunk_index"),
            "kind": metadata.get("kind") or ("table" if tables else "text"),
            "tables": tables,
        })

    context_str = "\n\n---\n\n".join(match["text"] for match in matches if match["text"])
    sources = sorted({match["source"] for match in matches if match["source"]})

    prompt = f"""Answer the question using ONLY the provided context below.
When a markdown table in the context answers the question, copy that table into the answer as a markdown table. Keep its header row and the relevant rows. Do not rewrite a table as a bullet list.

Context:
{context_str}

Question: {query_text}"""

    response = generate_response_with_retry(prompt)

    tables = []
    seen = set()
    for match in matches:
        for table in match["tables"]:
            key = (table["title"], tuple(table["headers"]), tuple(tuple(row) for row in table["rows"]))
            if key in seen:
                continue
            seen.add(key)
            tables.append(table)

    return {
        "answer": response.text or "",
        "sources": sources,
        "tables": tables,
        "matches": matches,
    }

if __name__ == "__main__":
    print("Pinecone Cloud RAG Ready! Ask a question (or 'exit' to quit):\n")
    while True:
        user_input = input("Question: ").strip()
        if user_input.lower() in ["exit", "quit", "q"]:
            break
        if user_input:
            result = query_rag(user_input)
            print("\n=== ANSWER ===")
            print(result["answer"])
            print("\n=== SOURCES RETRIEVED FROM PINECONE ===")
            for src in result["sources"]:
                print(f"- {src}")
            print("\n" + "="*40 + "\n")