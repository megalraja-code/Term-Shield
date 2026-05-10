import numpy as np, faiss
from sentence_transformers import SentenceTransformer
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)
_model = None
_faiss_store: Dict[int, Dict] = {}

def init_model():
    global _model
    _model = SentenceTransformer("all-MiniLM-L6-v2")
    logger.info("Embedding model ready")

def _m():
    if _model is None: init_model()
    return _model

def _chunk(text: str, size=350, overlap=50) -> List[str]:
    w = text.split(); chunks = []; i = 0
    while i < len(w):
        chunks.append(" ".join(w[i:i+size])); i += size-overlap
    return chunks

def build_index(aid: int, text: str):
    chunks = _chunk(text)
    if not chunks: return
    emb = _m().encode(chunks, convert_to_numpy=True, show_progress_bar=False).astype(np.float32)
    faiss.normalize_L2(emb)
    idx = faiss.IndexFlatIP(emb.shape[1]); idx.add(emb)
    _faiss_store[aid] = {"index": idx, "chunks": chunks}

def search_index(aid: int, query: str, top_k=5) -> List[Tuple[str, float]]:
    if aid not in _faiss_store: return []
    st = _faiss_store[aid]
    q  = _m().encode([query], convert_to_numpy=True).astype(np.float32)
    faiss.normalize_L2(q)
    sc, ids = st["index"].search(q, min(top_k, len(st["chunks"])))
    return [(st["chunks"][i], float(v)) for v, i in zip(sc[0], ids[0]) if i != -1 and v > 0.1]
