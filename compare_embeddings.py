import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def compare_texts(t1: str, t2: str):
    vec1 = model.encode(t1)
    vec2 = model.encode(t2)

    score = cosine_similarity(vec1, vec2)
    print(f"Text 1: '{t1}'")
    print(f"Text 2: '{t2}'")
    print(f"Local Similarity Score: {score:.4f}\n")

if __name__ == "__main__":
    compare_texts("The dog chased the ball.", "A puppy ran after the sphere.")
    compare_texts("The dog chased the ball.", "Quarterly earnings report.")