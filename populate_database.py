"""Index PDF files from ./data into a persistent Chroma database."""
import argparse
import shutil
from pathlib import Path
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_chroma import Chroma
from get_embedding_function import get_embedding_function

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data"
CHROMA_PATH = ROOT / "chroma"


def load_documents() -> list[Document]:
    DATA_PATH.mkdir(parents=True, exist_ok=True)
    pdfs = list(DATA_PATH.glob("*.pdf"))
    if not pdfs:
        raise SystemExit(f"Tidak ada PDF di {DATA_PATH}. Masukkan artikel ke folder data.")
    return PyPDFDirectoryLoader(str(DATA_PATH)).load()


def split_documents(documents: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=150, length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = splitter.split_documents(documents)
    for chunk in chunks:
        source = Path(chunk.metadata.get("source", "unknown.pdf")).name
        page = chunk.metadata.get("page", 0)
        # Stable IDs make rerunning indexing idempotent.
        import hashlib
        digest = hashlib.sha1(chunk.page_content.encode("utf-8")).hexdigest()[:12]
        chunk.metadata["source"] = source
        chunk.metadata["id"] = f"{source}:p{page}:{digest}"
    return chunks


def main():
    parser = argparse.ArgumentParser(description="Index PDF articles into ChromaDB")
    parser.add_argument("--reset", action="store_true", help="Delete and rebuild the local Chroma database")
    args = parser.parse_args()
    if args.reset and CHROMA_PATH.exists():
        shutil.rmtree(CHROMA_PATH)
        print("Database Chroma lama dihapus.")

    documents = load_documents()
    chunks = split_documents(documents)
    db = Chroma(persist_directory=str(CHROMA_PATH), embedding_function=get_embedding_function())
    existing = set(db.get(include=[]) ["ids"])
    new_chunks = [chunk for chunk in chunks if chunk.metadata["id"] not in existing]
    print(f"PDF pages loaded: {len(documents)} | chunks created: {len(chunks)}")
    print(f"Existing chunks: {len(existing)} | new chunks: {len(new_chunks)}")
    if new_chunks:
        db.add_documents(new_chunks, ids=[c.metadata["id"] for c in new_chunks])
        print("Selesai: dokumen baru disimpan ke ChromaDB.")
    else:
        print("Tidak ada dokumen baru. Gunakan --reset jika ingin membangun ulang indeks.")


if __name__ == "__main__":
    main()
