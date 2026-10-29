import os
from dotenv import load_dotenv
from google import genai
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()

INDEX_NAME = "rag-index"

# Initialize services
client = genai.Client()
model = SentenceTransformer("all-MiniLM-L6-v2")
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
    query_vector = model.encode(query_text).tolist()

    # 2. Query Pinecone Cloud index
    results = index.query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=True
    )

    matches = []
    for match in results["matches"]:
        metadata = match.get("metadata") or {}
        matches.append({
            "text": metadata.get("text", ""),
            "source": metadata.get("source", ""),
            "score": match.get("score"),
            "chunk_index": metadata.get("chunk_index"),
        })

    context_str = "\n\n---\n\n".join(match["text"] for match in matches if match["text"])
    sources = sorted({match["source"] for match in matches if match["source"]})

    prompt = f"""Answer the question using ONLY the provided context below.

Context:
{context_str}

Question: {query_text}"""

    response = generate_response_with_retry(prompt)

    return {
        "answer": response.text or "",
        "sources": sources,
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