"""
Embed review chunks with all-MiniLM-L6-v2 and store them in ChromaDB for semantic search.
"""

from __future__ import annotations

import chromadb
from sentence_transformers import SentenceTransformer

from ingest import Chunk, load_and_chunk

CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "professor_reviews"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
DEFAULT_TOP_K = 5
BATCH_SIZE = 64

EVAL_QUERIES = [
    "What grading policy do students mention for Tong Yi's CS135 class?",
    "How is Eric Schweitzer's grade broken down according to student reviews?",
    "Which Hunter CS professor do reviews describe as having a generous exam curve?",
]

_model: SentenceTransformer | None = None


def get_embedding_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    model = get_embedding_model()
    vectors = model.encode(texts, show_progress_bar=len(texts) > BATCH_SIZE)
    return vectors.tolist()


def chunk_id(chunk: Chunk) -> str:
    return f"{chunk.source_file}_{chunk.chunk_index}"


def get_client() -> chromadb.PersistentClient:
    # SegmentAPI avoids Rust binding crashes on some Windows setups (ChromaDB 1.5.x).
    return chromadb.PersistentClient(
        path=CHROMA_PATH,
        settings=chromadb.Settings(
            chroma_api_impl="chromadb.api.segment.SegmentAPI",
            anonymized_telemetry=False,
        ),
    )


def get_collection(client: chromadb.PersistentClient | None = None) -> chromadb.Collection:
    if client is None:
        client = get_client()
    return client.get_or_create_collection(name=COLLECTION_NAME)


def build_index(chunks: list[Chunk] | None = None, force: bool = False) -> chromadb.Collection:
    if chunks is None:
        chunks = load_and_chunk()

    client = get_client()

    if force and COLLECTION_NAME in [col.name for col in client.list_collections()]:
        client.delete_collection(COLLECTION_NAME)

    collection = get_collection(client)

    if not force and collection.count() == len(chunks):
        print(f"ChromaDB index already contains {collection.count()} chunks.")
        return collection

    if collection.count() > 0:
        client.delete_collection(COLLECTION_NAME)
        collection = get_collection(client)

    print(f"Embedding and storing {len(chunks)} chunks in ChromaDB...")

    for start in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[start : start + BATCH_SIZE]
        documents = [chunk.text for chunk in batch]
        collection.add(
            ids=[chunk_id(chunk) for chunk in batch],
            documents=documents,
            embeddings=embed_texts(documents),
            metadatas=[
                {
                    "source_file": chunk.source_file,
                    "source_url": chunk.source_url or "",
                    "professor": chunk.professor,
                    "class_name": chunk.class_name,
                    "chunk_index": chunk.chunk_index,
                    "review_number": chunk.review_number,
                }
                for chunk in batch
            ],
        )
        print(f"  Stored {min(start + BATCH_SIZE, len(chunks))}/{len(chunks)}")

    print(f"Done. Collection now has {collection.count()} chunks.")
    return collection


def retrieve(
    query: str,
    k: int = DEFAULT_TOP_K,
    collection: chromadb.Collection | None = None,
) -> list[dict]:
    if collection is None:
        collection = get_collection()

    if collection.count() == 0:
        raise RuntimeError("ChromaDB collection is empty. Run build_index() first.")

    query_embedding = embed_texts([query])
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )

    retrieved: list[dict] = []
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    for document, metadata, distance in zip(documents, metadatas, distances):
        retrieved.append(
            {
                "text": document,
                "distance": distance,
                "source_file": metadata.get("source_file", ""),
                "professor": metadata.get("professor", ""),
                "class_name": metadata.get("class_name", ""),
                "chunk_index": metadata.get("chunk_index", ""),
            }
        )

    return retrieved


def print_retrieval_results(query: str, results: list[dict]) -> None:
    print(f"\nQuery: {query}")
    print("-" * 72)
    if not results:
        print("No results returned.")
        return

    for rank, result in enumerate(results, start=1):
        preview = result["text"]
        if len(preview) > 400:
            preview = preview[:400] + "..."
        print(f"\nResult {rank} (distance: {result['distance']:.4f})")
        print(f"Professor: {result['professor']}")
        print(f"Source: {result['source_file']} | Class: {result['class_name']}")
        print(preview)


def run_eval_queries(collection: chromadb.Collection | None = None) -> None:
    print("\n" + "=" * 72)
    print("RETRIEVAL TESTS (Milestone 4 eval questions 1, 2, and 4)")
    print("=" * 72)

    for query in EVAL_QUERIES:
        results = retrieve(query, k=DEFAULT_TOP_K, collection=collection)
        print_retrieval_results(query, results)


def main() -> None:
    collection = build_index()
    run_eval_queries(collection)


if __name__ == "__main__":
    main()
