"""Ask a question against indexed PDF articles."""
import argparse
from pathlib import Path
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from get_embedding_function import get_embedding_function

ROOT = Path(__file__).resolve().parent
CHROMA_PATH = ROOT / "chroma"
LLM_MODEL = "mistral"
PROMPT = """Anda adalah asisten riset akademik. Jawab dalam bahasa Indonesia hanya berdasarkan konteks.
Jika konteks tidak cukup, nyatakan bahwa informasi tidak ditemukan. Jangan mengarang fakta atau sumber.
Sertakan nama file dan nomor halaman jika tersedia.

KONTEKS:
{context}

PERTANYAAN: {question}

Jawaban berbasis bukti:"""


def query_rag(question: str, k: int = 5):
    if not CHROMA_PATH.exists() or not any(CHROMA_PATH.iterdir()):
        raise SystemExit("Database belum tersedia. Jalankan: python populate_database.py")
    db = Chroma(persist_directory=str(CHROMA_PATH), embedding_function=get_embedding_function())
    results = db.similarity_search_with_score(question, k=k)
    if not results:
        print("Tidak ditemukan dokumen yang relevan.")
        return
    context = "\n\n---\n\n".join(
        f"Sumber: {doc.metadata.get('source', 'unknown')} | Halaman: {doc.metadata.get('page', 'n/a')}\n{doc.page_content}"
        for doc, _ in results
    )
    prompt = ChatPromptTemplate.from_template(PROMPT).format(context=context, question=question)
    answer = ChatOllama(model=LLM_MODEL, temperature=0).invoke(prompt).content
    print("\n=== JAWABAN ===\n" + answer)
    print("\n=== SUMBER YANG DIAMBIL ===")
    for doc, score in results:
        print(f"- {doc.metadata.get('source')} | halaman {doc.metadata.get('page', 'n/a')} | distance={score:.4f}")
    return answer


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", help="Pertanyaan untuk dokumen PDF")
    parser.add_argument("-k", type=int, default=5, help="Jumlah potongan dokumen yang diambil")
    args = parser.parse_args()
    query_rag(args.query_text, args.k)
