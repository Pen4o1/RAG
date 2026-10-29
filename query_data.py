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

def query_rag(query_text: str, top_k: int = 5):
    # 1. Embed query vector locally
    query_vector = model.encode(query_text).tolist()

    # 2. Query Pinecone Cloud index
    results = index.query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=True
    )

    retrieved_chunks = [match["metadata"]["text"] for match in results["matches"]]
    sources = list(set(match["metadata"]["source"] for match in results["matches"]))

    context_str = "\n\n---\n\n".join(retrieved_chunks)

    prompt = f"""Answer the question using ONLY the provided context below.

Context:
{context_str}

Question: {query_text}"""

    response = generate_response_with_retry(prompt)

    print("\n=== ANSWER ===")
    print(response.text)
    print("\n=== SOURCES RETRIEVED FROM PINECONE ===")
    for src in sources:
        print(f"- {src}")

if __name__ == "__main__":
    print("Pinecone Cloud RAG Ready! Ask a question (or 'exit' to quit):\n")
    while True:
        user_input = input("Question: ").strip()
        if user_input.lower() in ["exit", "quit", "q"]:
            break
        if user_input:
            query_rag(user_input)
            print("\n" + "="*40 + "\n")