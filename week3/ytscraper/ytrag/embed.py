"""Pluggable embedder.

One backend today (sentence-transformers), but everything downstream talks to
the Protocol, so swapping the model is a config change plus `ytrag reindex`.
"""

import contextlib
import io
import re
import sys
from typing import Protocol

from ytrag.config import EMBED_BATCH, EMBED_MODEL, EMBED_QUERY_PREFIX

# Noise the model loader prints from a compiled extension, which no env var
# turns off. Filtered rather than suppressed wholesale: anything that is not
# one of these still reaches stderr, so real failures are never hidden.
_BENIGN = re.compile(
    r"unauthenticated requests to the HF Hub|Loading weights:|^\s*$"
)


@contextlib.contextmanager
def _quiet_load():
    """Swallow the known-benign loader chatter, re-emit everything else."""
    captured = io.StringIO()
    try:
        with contextlib.redirect_stderr(captured):
            yield
    finally:
        for line in captured.getvalue().splitlines():
            if not _BENIGN.search(line):
                print(line, file=sys.stderr)


class Embedder(Protocol):
    name: str
    dim: int

    def embed_documents(self, texts: list[str]) -> list[list[float]]: ...

    def embed_query(self, text: str) -> list[float]: ...


class SentenceTransformerEmbedder:
    """Local embeddings. Default is bge-m3 (1024-dim, multilingual).

    bge-m3 needs no instruction prefix. Some other models do, and only on the
    query side — bge-*-en-v1.5 wants "Represent this sentence for searching
    relevant passages: ". That is what EMBED_QUERY_PREFIX is for. Getting this
    wrong degrades results silently: no error, just worse answers.
    """

    def __init__(self, model_name: str = EMBED_MODEL, batch_size: int = EMBED_BATCH):
        from sentence_transformers import SentenceTransformer

        self.name = model_name
        self.batch_size = batch_size
        with _quiet_load():
            self.model = SentenceTransformer(model_name)
        # Renamed in sentence-transformers 6; keep working on older pins too.
        get_dim = getattr(self.model, "get_embedding_dimension", None) or (
            self.model.get_sentence_embedding_dimension
        )
        self.dim = int(get_dim())

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        vectors = self.model.encode(
            texts,
            batch_size=self.batch_size,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return [v.tolist() for v in vectors]

    def embed_query(self, text: str) -> list[float]:
        vector = self.model.encode(
            EMBED_QUERY_PREFIX + text,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return vector.tolist()


_EMBEDDER: Embedder | None = None


def get_embedder() -> Embedder:
    """Load the embedder once per process — the model is 2.2GB."""
    global _EMBEDDER
    if _EMBEDDER is None:
        _EMBEDDER = SentenceTransformerEmbedder()
    return _EMBEDDER
