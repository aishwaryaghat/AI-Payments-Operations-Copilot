"""Local FAISS vector index for synthetic runbooks.

Index rebuilding is deterministic for the source set and embedding model.
Persist only in a trusted local directory: document embeddings can be sensitive.
"""
import hashlib
import os
from pathlib import Path
from functools import lru_cache
import numpy as np

def _index_dir() -> Path:
    return Path(os.getenv("COPILOT_VECTOR_DIR", ".copilot_vectors"))

@lru_cache(maxsize=4)
def build_index(corpus_fingerprint: str, vectors_shape: tuple, vectors_bytes: bytes):
    import faiss
    vectors = np.frombuffer(vectors_bytes, dtype=np.float32).reshape(vectors_shape).copy()
    index = faiss.IndexFlatIP(vectors_shape[1])
    index.add(vectors)
    folder = _index_dir()
    folder.mkdir(parents=True, exist_ok=True)
    # Synthetic corpus only. Index filename also captures model and corpus versions.
    path = folder / (corpus_fingerprint + ".faiss")
    faiss.write_index(index, str(path))
    return index

def nearest(query_vector, document_vectors, corpus_texts, model_name: str, k: int):
    import faiss
    documents = np.asarray(document_vectors, dtype=np.float32)
    query = np.asarray(query_vector, dtype=np.float32).reshape(1, -1)
    if documents.shape[0] != len(corpus_texts):
        raise ValueError("Vector-document count mismatch")
    digest = hashlib.sha256(
        (model_name + "\n" + "\n".join(corpus_texts)).encode("utf-8")
    ).hexdigest()[:20]
    folder = _index_dir()
    path = folder / (digest + ".faiss")
    if path.exists():
        index = faiss.read_index(str(path))
        if index.d != documents.shape[1] or index.ntotal != documents.shape[0]:
            index = build_index(digest, documents.shape, documents.tobytes())
    else:
        index = build_index(digest, documents.shape, documents.tobytes())
    scores, ids = index.search(query, min(k, len(corpus_texts)))
    return [(int(i), float(score)) for i, score in zip(ids[0], scores[0]) if i >= 0]
