from pathlib import Path

import numpy as np
from fastembed import TextEmbedding

model = TextEmbedding(
    "sentence-transformers/all-MiniLM-L6-v2",
    cache_dir=str(Path(__file__).resolve().parent / ".cache" / "fastembed"),
    threads=1,
    providers=["CPUExecutionProvider"],
)

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def compare_texts(t1: str, t2: str):
    vec1 = next(model.embed([t1]))
    vec2 = next(model.embed([t2]))

    score = cosine_similarity(vec1, vec2)
    print(f"Text 1: '{t1}'")
    print(f"Text 2: '{t2}'")
    print(f"Local Similarity Score: {score:.4f}\n")

if __name__ == "__main__":
    compare_texts("The dog chased the ball.", "A puppy ran after the sphere.")
    compare_texts("The dog chased the ball.", "Quarterly earnings report.")