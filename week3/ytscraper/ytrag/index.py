"""Qdrant upsert + query.

Same client as day14/day15, but with two differences that matter at this scale:
the collection name carries the embedding dim, and point IDs are derived from
a stable chunk_id so re-ingesting overwrites instead of duplicating.
"""

import atexit
import json
import re
import uuid
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PayloadSchemaType,
    PointStruct,
    VectorParams,
)

from ytrag.config import (
    COLLECTION,
    MAX_DISTANCE,
    QDRANT_API_KEY,
    QDRANT_PATH,
    QDRANT_URL,
    TITLE_BOOST,
    TOP_K,
    UPSERT_BATCH,
)
from ytrag.embed import get_embedder
from ytrag.models import Chunk, _NAMESPACE
from ytrag.util import with_retry

_CLIENT: QdrantClient | None = None


def _close_client() -> None:
    """Release the store before the interpreter tears down.

    Qdrant's own __del__ runs during shutdown, by which point sys.meta_path is
    gone and its close() raises ImportError. Harmless, but it prints a
    traceback after a successful command and looks like a crash.
    """
    global _CLIENT
    if _CLIENT is not None:
        try:
            _CLIENT.close()
        except Exception:
            pass
        _CLIENT = None


atexit.register(_close_client)


def get_client() -> QdrantClient:
    """Qdrant Cloud when configured, otherwise an embedded local store.

    The local mode matters more than it looks: it means someone can clone this
    repo and have a working index with no Qdrant account, no Docker, and no
    signup — just a folder on disk. QDRANT_URL upgrades them to the hosted
    cluster whenever they want one.
    """
    global _CLIENT
    if _CLIENT is None:
        if QDRANT_URL:
            _CLIENT = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY or None)
        else:
            QDRANT_PATH.mkdir(parents=True, exist_ok=True)
            try:
                _CLIENT = QdrantClient(path=str(QDRANT_PATH))
            except RuntimeError as exc:
                # The embedded store is a single-writer file lock, so a second
                # command while `ytrag serve` is running fails with a message
                # that explains nothing. Say what actually happened.
                if "already accessed" in str(exc) or "Storage folder" in str(exc):
                    raise RuntimeError(
                        "The local index is already open in another process — most likely "
                        "`ytrag serve` is running in another terminal. Stop it (Ctrl-C) and "
                        "try again, or set QDRANT_URL to use a hosted Qdrant which allows "
                        "many readers at once."
                    ) from exc
                raise
    return _CLIENT


def collection_name() -> str:
    """e.g. 'dsa_lectures_1024'.

    Qdrant rejects vectors whose size does not match the collection, so
    stamping the dim into the name means switching embedding models creates a
    new collection instead of erroring — and lets a 1024-dim local index and a
    384-dim deploy index live side by side.
    """
    return f"{COLLECTION}_{get_embedder().dim}"


def ensure_collection() -> str:
    """Create the collection if it does not exist. Safe to call every time."""
    client = get_client()
    name = collection_name()

    if not client.collection_exists(name):
        client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(
                size=get_embedder().dim,
                distance=Distance.COSINE,
            ),
        )
        # Only meaningful on a Qdrant server — the embedded store filters
        # without an index and warns if you ask for one.
        if QDRANT_URL:
            client.create_payload_index(
                collection_name=name,
                field_name="video_id",
                field_schema=PayloadSchemaType.KEYWORD,
            )
    return name


def upsert_chunks(chunks: list[Chunk], batch_size: int = UPSERT_BATCH) -> int:
    """Embed and upsert. Idempotent: same chunk_id -> same point ID -> overwrite."""
    if not chunks:
        return 0

    name = ensure_collection()
    client = get_client()
    embedder = get_embedder()

    total = 0
    for start in range(0, len(chunks), batch_size):
        batch = chunks[start : start + batch_size]
        vectors = embedder.embed_documents([c.text for c in batch])
        points = [
            PointStruct(id=c.point_id, vector=v, payload=c.to_payload())
            for c, v in zip(batch, vectors)
        ]
        # Retried for the same reason downloads are: this is a network call in
        # the middle of a long unattended run. Upsert is idempotent, so a
        # retry after a partial success is harmless.
        with_retry(
            lambda: client.upsert(collection_name=name, points=points, wait=True),
            label=f"upsert {len(points)} points",
        )
        total += len(points)

    return total


def delete_video(video_id: str) -> None:
    """Remove every chunk for one video. Used when re-chunking with new settings."""
    client = get_client()
    name = ensure_collection()
    client.delete(
        collection_name=name,
        points_selector=Filter(
            must=[FieldCondition(key="video_id", match=MatchValue(value=video_id))]
        ),
        wait=True,
    )


def indexed_video_ids() -> set[str]:
    """Which videos already have chunks in the collection.

    Lets a re-run skip the embed+upsert for work already done. Without this,
    restarting a partly-finished ingest re-embeds every cached transcript
    before reaching new material — minutes of idle GPU each time.
    """
    client = get_client()
    name = collection_name()
    if not client.collection_exists(name):
        return set()

    found: set[str] = set()
    offset = None
    while True:
        points, offset = client.scroll(
            collection_name=name,
            limit=1000,
            offset=offset,
            with_payload=["video_id"],
            with_vectors=False,
        )
        for point in points:
            if point.payload and point.payload.get("video_id"):
                found.add(point.payload["video_id"])
        if offset is None:
            break
    return found


# Words that carry no topic signal — Hinglish question scaffolding, plus the
# boilerplate that appears in almost every lecture title.
_STOP = {
    "kaise", "kya", "hai", "hain", "me", "ka", "ki", "ke", "aur", "kab", "karte",
    "karna", "hota", "nikale", "solve", "kare", "chahiye", "use", "kahan", "se",
    "ko", "pehchane", "difference", "farak", "the", "a", "is", "in", "what", "how",
    "do", "to", "of", "for", "video", "dsa", "patterns", "pattern", "episode",
    "leetcode", "interview", "questions", "question", "master", "best", "explained",
}


def _stem(word: str) -> str:
    """Crude plural stripping, enough to match 'hashmap' against 'HASHMAPS'."""
    for suffix in ("es", "s"):
        if len(word) > 4 and word.endswith(suffix):
            return word[: -len(suffix)]
    return word


def _terms(text: str) -> set[str]:
    return {
        _stem(w)
        for w in re.findall(r"[a-z0-9]+", text.lower())
        if w not in _STOP and len(w) > 2
    }


def title_overlap(query: str, title: str) -> int:
    """How many meaningful query words appear in the lecture's title."""
    return len(_terms(query) & _terms(title))


def search(
    query: str,
    top_k: int = TOP_K,
    video_id: str | None = None,
    max_distance: float | None = None,
) -> list[tuple[Chunk, float]]:
    """Return [(chunk, distance)] sorted best-first, already distance-filtered.

    Qdrant returns a cosine *similarity* score (higher is better); the rest of
    the system thinks in distance (lower is better), so convert once here.
    """
    name = ensure_collection()
    client = get_client()
    vector = get_embedder().embed_query(query)

    query_filter = None
    if video_id:
        query_filter = Filter(
            must=[FieldCondition(key="video_id", match=MatchValue(value=video_id))]
        )

    # Over-fetch, then re-rank. The vector search alone is a decent recall
    # filter but a poor judge of which result belongs first.
    results = client.query_points(
        collection_name=name,
        query=vector,
        limit=max(top_k * 4, 20),
        with_payload=True,
        query_filter=query_filter,
    ).points

    cutoff = MAX_DISTANCE if max_distance is None else max_distance
    scored: list[tuple[float, float, Chunk]] = []
    for point in results:
        distance = 1.0 - float(point.score)
        if distance > cutoff:
            continue
        chunk = Chunk.from_payload(point.payload)
        # Nudge chunks whose lecture title actually mentions what was asked.
        # Dense similarity over a 75-second ramble dilutes the topic badly —
        # a chunk about ASCII values outranked the Number of Islands lecture
        # for "number of islands" until this existed. The title is the one
        # place the topic is stated plainly, so it gets a say in the ordering.
        # Measured on 12 questions: top-1 accuracy 9/12 -> 12/12.
        overlap = title_overlap(query, chunk.video_title)
        scored.append((distance - TITLE_BOOST * overlap, distance, chunk))

    scored.sort(key=lambda row: row[0])
    return [(chunk, distance) for _, distance, chunk in scored[:top_k]]


def stats() -> dict:
    """Collection size plus a per-video breakdown."""
    client = get_client()
    name = collection_name()

    if not client.collection_exists(name):
        return {"collection": name, "exists": False, "chunks": 0, "videos": {}}

    info = client.get_collection(name)
    videos: dict[str, dict] = {}

    offset = None
    while True:
        points, offset = client.scroll(
            collection_name=name,
            limit=512,
            offset=offset,
            with_payload=["video_id", "video_title"],
            with_vectors=False,
        )
        for point in points:
            payload = point.payload or {}
            vid = payload.get("video_id", "?")
            entry = videos.setdefault(vid, {"title": payload.get("video_title", "?"), "chunks": 0})
            entry["chunks"] += 1
        if offset is None:
            break

    return {
        "collection": name,
        "exists": True,
        "chunks": info.points_count or 0,
        "dim": get_embedder().dim,
        "embed_model": get_embedder().name,
        "videos": videos,
    }


# ------------------------------------------------------------------
# Shipping a prebuilt index
# ------------------------------------------------------------------
# Embedding 2933 chunks takes a couple of minutes on a decent CPU and rather
# longer on a weak laptop. The vectors themselves are small — 2933 x 384
# float16 is about 2 MB — so committing them means someone can clone the repo
# and have a working index in seconds, without ever running the encoder over
# the corpus. They still need the model to embed their own *queries*, which is
# why the small one matters.

def export_vectors(path: Path) -> dict:
    """Dump every point's vector and payload to a compressed .npz."""
    import numpy as np

    client = get_client()
    name = collection_name()
    vectors, payloads = [], []

    offset = None
    while True:
        points, offset = client.scroll(
            collection_name=name, limit=512, offset=offset,
            with_payload=True, with_vectors=True,
        )
        for point in points:
            vectors.append(point.vector)
            payloads.append(point.payload)
        if offset is None:
            break

    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        path,
        vectors=np.array(vectors, dtype=np.float16),
        payloads=np.array(json.dumps(payloads)),
        model=np.array(get_embedder().name),
        dim=np.array(get_embedder().dim),
    )
    return {"count": len(vectors), "mb": path.stat().st_size / 1024 / 1024}


def import_vectors(path: Path, batch_size: int = UPSERT_BATCH) -> dict:
    """Load a .npz built by export_vectors straight into the collection.

    Refuses to load vectors built by a different embedding model — mixing them
    would silently wreck retrieval, since a query encoded by one model is
    meaningless against another's vectors.
    """
    import numpy as np

    data = np.load(path, allow_pickle=False)
    model = str(data["model"])
    if model != get_embedder().name:
        raise RuntimeError(
            f"These vectors were built with {model}, but YTRAG_EMBED_MODEL is "
            f"{get_embedder().name}. Set YTRAG_EMBED_MODEL={model}, or run "
            f"`ytrag reindex` to rebuild with your model."
        )

    vectors = data["vectors"].astype("float32")
    payloads = json.loads(str(data["payloads"]))
    name = ensure_collection()
    client = get_client()

    for start in range(0, len(vectors), batch_size):
        chunk_payloads = payloads[start : start + batch_size]
        points = [
            PointStruct(
                id=str(uuid.uuid5(_NAMESPACE, p["chunk_id"])),
                vector=v.tolist(),
                payload=p,
            )
            for v, p in zip(vectors[start : start + batch_size], chunk_payloads)
        ]
        client.upsert(collection_name=name, points=points, wait=True)

    return {"count": len(vectors), "model": model}
