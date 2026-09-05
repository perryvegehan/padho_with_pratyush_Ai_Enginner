"""All tunables live here, every one of them env-driven.

Nothing else in the package reads os.getenv directly.
"""

import logging
import os
from pathlib import Path

from dotenv import find_dotenv, load_dotenv

# huggingface_hub warns on every model load that requests are unauthenticated.
# It is advice about download rate limits, not a problem, and it makes a
# working first run look like it failed.
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

# ------------------------------------------------------------------
# .env loading
# ------------------------------------------------------------------
# Keys (GROQ_API_KEY, QDRANT_URL, QDRANT_API_KEY) live in the repo-root .env,
# same as every other week. Look in the cwd chain first, then fall back to
# walking up from this file so `ytrag` works from any directory.
load_dotenv(find_dotenv(usecwd=True))

_REPO_ROOT = Path(__file__).resolve().parents[3]
_ROOT_ENV = _REPO_ROOT / ".env"
if _ROOT_ENV.exists():
    load_dotenv(_ROOT_ENV, override=False)


# ------------------------------------------------------------------
# Runtime data directories
# ------------------------------------------------------------------
# These live OUTSIDE the repo. The split matters:
#   audio/       deletable, regenerable in seconds
#   transcripts/ precious, hours of GPU time, never delete
# Everything downstream of transcripts is cheap to rebuild, which is why
# changing your mind about the embedding model later costs nothing.
ROOT = Path(os.getenv("YTRAG_ROOT", Path.home() / ".ytrag"))
AUDIO_DIR = ROOT / "audio"
TRANSCRIPT_DIR = ROOT / "transcripts"

for _d in (AUDIO_DIR, TRANSCRIPT_DIR):
    _d.mkdir(parents=True, exist_ok=True)


# ------------------------------------------------------------------
# Transcription
# ------------------------------------------------------------------
# faster-whisper (CTranslate2), not mlx-whisper — this is a Windows/CUDA box.
WHISPER_MODEL = os.getenv("YTRAG_WHISPER_MODEL", "large-v3")
WHISPER_DEVICE = os.getenv("YTRAG_WHISPER_DEVICE", "auto")  # auto | cuda | cpu
WHISPER_COMPUTE = os.getenv("YTRAG_WHISPER_COMPUTE", "")  # blank = pick per device
WHISPER_LANG = os.getenv("YTRAG_WHISPER_LANG", "en")  # see README §6.0 — TEST THIS FIRST
WHISPER_BEAM = int(os.getenv("YTRAG_WHISPER_BEAM", 5))
# Batched inference transcribes several VAD-detected speech regions at once.
# Same model, same weights, several times the throughput — the difference
# between an overnight run and an afternoon one on 68 hours of lecture.
# Set to 0 to fall back to the sequential path.
WHISPER_BATCH = int(os.getenv("YTRAG_WHISPER_BATCH", 8))


# ------------------------------------------------------------------
# Chunking
# ------------------------------------------------------------------
# 75s is roughly one explained idea (~180-220 words of speech).
CHUNK_SECONDS = int(os.getenv("YTRAG_CHUNK_SECONDS", 75))
CHUNK_OVERLAP_SECONDS = int(os.getenv("YTRAG_CHUNK_OVERLAP", 15))
MIN_CHUNK_WORDS = int(os.getenv("YTRAG_MIN_CHUNK_WORDS", 15))
# Retrieval hits the chunk containing the answer, but the explanation usually
# starts just before it. Rewind the citation link by a few seconds.
LINK_REWIND_SECONDS = int(os.getenv("YTRAG_LINK_REWIND", 5))


# ------------------------------------------------------------------
# Embeddings
# ------------------------------------------------------------------
# all-MiniLM-L6-v2 by default, and the reasoning is worth keeping.
#
# bge-m3 is the "better" model on paper — multilingual, built for exactly this
# code-switched Hinglish problem. But measured on this corpus of 2933 chunks:
#
#            download   index (CPU)   top-1    top-5
#   bge-m3     4.35 GB     55 min     12/12    12/12
#   MiniLM       87 MB    1.6 min     11/12    12/12
#
# One question differs, and it still comes back at rank 2. Fifty times smaller
# and thirty times faster for that. The title-boost re-ranking in index.py
# recovers most of what the smaller model gives up, which is why the gap is so
# narrow — better ranking turned out to be worth more than a bigger encoder.
#
# Set YTRAG_EMBED_MODEL=BAAI/bge-m3 and reindex if you want the last 1/12.
EMBED_MODEL = os.getenv("YTRAG_EMBED_MODEL", "all-MiniLM-L6-v2")
EMBED_BATCH = int(os.getenv("YTRAG_EMBED_BATCH", 16))
# Some models want an instruction prefixed to the *query only*. bge-m3 does
# not; bge-*-en-v1.5 does. If you switch models, check the model card.
EMBED_QUERY_PREFIX = os.getenv("YTRAG_EMBED_QUERY_PREFIX", "")


# ------------------------------------------------------------------
# Vector store (Qdrant, same as day14 / day15)
# ------------------------------------------------------------------
# YouTube starts challenging bulk downloaders after a few dozen videos
# ("Sign in to confirm you're not a bot"). A short random pause between
# downloads keeps us under that radar; it costs minutes across a whole
# playlist and avoids losing the run to a rate limit.
DOWNLOAD_SLEEP_MIN = float(os.getenv("YTRAG_DOWNLOAD_SLEEP_MIN", 2))
DOWNLOAD_SLEEP_MAX = float(os.getenv("YTRAG_DOWNLOAD_SLEEP_MAX", 6))
# If you get challenged persistently, send YouTube cookies.
#
# YTRAG_COOKIES_FROM_BROWSER works for Firefox, but NOT for Chrome or Edge on
# Windows: since Chrome 127 they encrypt cookies with App-Bound Encryption and
# yt-dlp cannot decrypt them (yt-dlp issue #10927). For Chromium browsers use
# YTRAG_COOKIES_FILE instead — export cookies.txt with a "Get cookies.txt"
# browser extension and point this at the file.
COOKIES_FROM_BROWSER = os.getenv("YTRAG_COOKIES_FROM_BROWSER", "")
COOKIES_FILE = os.getenv("YTRAG_COOKIES_FILE", "")


# Leave QDRANT_URL unset and the index lives in a local folder instead — no
# account, no Docker, no signup. Set it to use a hosted Qdrant cluster.
QDRANT_URL = os.getenv("QDRANT_URL", "")
QDRANT_PATH = Path(os.getenv("YTRAG_QDRANT_PATH", ROOT / "qdrant"))
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")
# The collection name carries the embedding dim, so switching embedding
# models can never hit a dimension-mismatch error against a live collection,
# and a local index and a deploy index can coexist in the same cluster.
COLLECTION = os.getenv("YTRAG_COLLECTION", "dsa_lectures")
UPSERT_BATCH = int(os.getenv("YTRAG_UPSERT_BATCH", 128))


# ------------------------------------------------------------------
# Retrieval + answering
# ------------------------------------------------------------------
TOP_K = int(os.getenv("YTRAG_TOP_K", 6))
# Cosine distance = 1 - score. Results further than this are dropped before
# the LLM sees them.
#
# 0.60, measured against 20 in-syllabus and 10 off-topic questions on the full
# 2933-chunk index. The two populations OVERLAP — the worst genuine question
# ("number of islands", 0.568) scores worse than the best off-topic one
# ("neural network backpropagation", 0.409) — so no single cutoff can separate
# them. Tightening it to 0.50 silently refused real questions like "hashmap kab
# use karna chahiye"; that is a worse failure than letting a junk chunk reach
# the LLM, because the student is told their own lecture doesn't exist.
#
# So this is a coarse pre-filter, not the real guard. It removes the obviously
# unrelated and keeps every genuine question; the model's own refusal, working
# from the excerpts, does the semantic judgement. Measured at this value:
# 20/20 real questions kept, 10/10 off-topic questions still refused.
MAX_DISTANCE = float(os.getenv("YTRAG_MAX_DISTANCE", 0.6))

# Below this, the top hit is a solid match and the UI says so plainly. Above
# it the results are still shown, just flagged as weak — measured in-syllabus
# questions land at 0.30-0.57, so this catches most genuine ones while marking
# the tail honestly.
CONFIDENT_DISTANCE = float(os.getenv("YTRAG_CONFIDENT_DISTANCE", 0.45))

# How much a matching word in the lecture title improves a chunk's ranking,
# in cosine-distance terms, per matched word. 0.06 is roughly one rank step
# in the tightly-clustered band bge-m3 produces. Set to 0 to disable.
TITLE_BOOST = float(os.getenv("YTRAG_TITLE_BOOST", 0.06))

# The written explanation is OPTIONAL — /search returns the timestamps without
# ever touching an LLM. This only configures the "explain" button.
#
# gemini is the default because its free tier is far more generous than Groq's
# (Groq caps at ~200k tokens/day, which one classroom exhausts in an hour).
_DEFAULT_BACKEND = (
    "gemini"
    if (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
    else ("groq" if os.getenv("GROQ_API_KEY") else "none")
)
LLM_BACKEND = os.getenv("YTRAG_LLM_BACKEND", _DEFAULT_BACKEND)  # gemini | groq | none
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")
LLM_MODEL = os.getenv("YTRAG_LLM_MODEL", "")  # blank = per-backend default
GROQ_MODEL = os.getenv("YTRAG_GROQ_MODEL", "openai/gpt-oss-120b")
GEMINI_MODEL = os.getenv("YTRAG_GEMINI_MODEL", "gemini-2.0-flash")

# The exact string the system says when retrieval comes back empty. Kept here
# because evaluate.py and the frontend both need to recognise it.
REFUSAL = "Ye topic in lectures me cover nahi hua."


# ------------------------------------------------------------------
# API (Phase 3/4)
# ------------------------------------------------------------------
MAX_QUESTION_CHARS = int(os.getenv("YTRAG_MAX_QUESTION_CHARS", 500))
RATE_LIMIT_REQUESTS = int(os.getenv("YTRAG_RATE_LIMIT_REQUESTS", 20))
RATE_LIMIT_WINDOW_SECONDS = int(os.getenv("YTRAG_RATE_LIMIT_WINDOW", 60))
