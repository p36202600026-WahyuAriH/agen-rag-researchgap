"""Basic environment and Ollama embedding smoke test."""
from get_embedding_function import get_embedding_function

if __name__ == "__main__":
    print("Menguji Ollama embedding...")
    vector = get_embedding_function().embed_query("uji embedding untuk artikel penelitian")
    print(f"OK: embedding berhasil dibuat, dimensi={len(vector)}")
