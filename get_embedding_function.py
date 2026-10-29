"""Embedding function using Ollama locally."""
from langchain_ollama import OllamaEmbeddings

EMBEDDING_MODEL = "nomic-embed-text"


def get_embedding_function():
    return OllamaEmbeddings(model=EMBEDDING_MODEL)
