from ..nlp.embeddings import EmbeddingModel
from ..vectorstore.local_numpy_store import LocalNumpyVectorStore


def search(query: str, top_k: int = 5):
    model = EmbeddingModel()
    emb = model.encode([query])[0]
    store = LocalNumpyVectorStore(dim=emb.shape[0])
    results = store.search(emb, top_k=top_k)

    print(f"[INFO] Query: {query}")
    print(f"[INFO] Found {len(results)} results:")
    for r in results:
        print(f"- id={r['id']} score={r['score']:.3f} payload={r['payload']}")


if __name__ == "__main__":
    search("Packaging issues and delayed Super 150s shipments from Rome to Milan", top_k=5)
