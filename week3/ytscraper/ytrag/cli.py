"""typer entrypoint.

    ytrag langtest <url>              # decide the Whisper language flag (do this first)
    ytrag ingest --playlist <URL>     # download -> transcribe -> chunk -> upsert
    ytrag ask "question"
    ytrag search "question"           # retrieval only, no LLM
    ytrag reindex                     # re-chunk + re-embed from cached transcripts
    ytrag stats
    ytrag eval
    ytrag serve                       # FastAPI + web UI
"""

import json
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table

from ytrag import config
from ytrag.answer import answer as answer_question
from ytrag.answer import retrieve_only
from ytrag.chunk import chunk_segments
from ytrag.evaluate import DEFAULT_GOLDEN, run_eval
from ytrag.embed import get_embedder
from ytrag.index import (
    delete_video,
    ensure_collection,
    get_client,
    indexed_video_ids,
    stats as index_stats,
    upsert_chunks,
)
from ytrag.models import Video, format_timestamp
from ytrag.playlist import download_audio, list_playlist
from ytrag.util import network_up, wait_for_network
from ytrag.transcribe import (
    cached_video_ids,
    get_model,
    load_transcript,
    run_whisper,
    segments_from_transcript,
    transcribe,
    transcript_path,
)

# Windows consoles still default to cp1252, which cannot encode the box-drawing
# and arrow characters rich uses — output crashes with UnicodeEncodeError partway
# through a table. Force UTF-8 before anything prints.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

app = typer.Typer(add_completion=False, help="Timestamp-level RAG over a YouTube lecture playlist.")
console = Console()

# How many times one video may be retried purely because the network was down.
# Generous, because each retry only happens after the connection has actually
# come back, so this bounds pathological flapping rather than honest outages.
MAX_NETWORK_RETRIES = 20


def _progress() -> Progress:
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
        console=console,
    )


# ------------------------------------------------------------------
# ingest
# ------------------------------------------------------------------
@app.command()
def ingest(
    playlist: str = typer.Option(..., "--playlist", "-p", help="Playlist or video URL."),
    limit: int = typer.Option(0, "--limit", "-n", help="Only process the first N videos."),
    skip_transcribe: bool = typer.Option(
        False, "--skip-transcribe", help="Only use videos that already have a cached transcript."
    ),
    keep_audio: bool = typer.Option(False, "--keep-audio", help="Don't delete audio after transcribing."),
    force: bool = typer.Option(False, "--force", help="Re-transcribe even if a transcript exists."),
    stop_after_failures: int = typer.Option(
        5,
        "--stop-after-failures",
        help="Abort if this many videos fail in a row (0 = never abort). "
        "Consecutive failures almost always mean the network is down.",
    ),
):
    """Download, transcribe, chunk and index a playlist. Safe to re-run."""
    console.print(f"[bold]Listing[/bold] {playlist}")
    videos = list_playlist(playlist)
    if limit:
        videos = videos[:limit]
    console.print(f"Found [bold]{len(videos)}[/bold] videos.\n")

    already_indexed = set() if force else indexed_video_ids()
    if already_indexed:
        console.print(f"[dim]{len(already_indexed)} video(s) already indexed — will skip.[/dim]\n")

    indexed = 0
    failures: list[tuple[str, str]] = []
    skipped = 0
    done = 0
    consecutive_failures = 0
    aborted = False

    with _progress() as progress:
        task = progress.add_task("Ingesting", total=len(videos))
        for video in videos:
            progress.update(task, description=f"[cyan]{video.title[:48]}")
            network_retries = 0

            # Inner loop so a video that failed only because the connection
            # dropped can be retried once the connection returns, rather than
            # being written off as a bad video.
            while True:
                try:
                    cached = load_transcript(video.video_id)

                    if skip_transcribe and cached is None:
                        skipped += 1
                        break

                    # Already transcribed AND already in the index: nothing to
                    # do. Skipping here is what makes a restart resume in
                    # seconds instead of re-embedding everything first.
                    if cached is not None and not force and video.video_id in already_indexed:
                        done += 1
                        consecutive_failures = 0
                        break

                    if cached is not None and not force:
                        segments = segments_from_transcript(cached)
                        video.title = cached.get("title") or video.title
                    else:
                        segments = transcribe(video, force=force, keep_audio=keep_audio)

                    chunks = chunk_segments(video, segments)
                    if chunks:
                        upsert_chunks(chunks)
                        indexed += len(chunks)

                    consecutive_failures = 0
                    done += 1
                    progress.console.print(
                        f"  [green]ok[/green] {video.title[:52]} — {len(chunks)} chunks"
                    )
                    break

                except KeyboardInterrupt:
                    # Ctrl-C stops here rather than being swallowed as a
                    # failure. Everything already transcribed stays cached.
                    aborted = True
                    progress.console.print("\n[yellow]Interrupted — cached work is safe.[/yellow]")
                    break

                except Exception as exc:
                    # Distinguish "this video is bad" from "the internet is
                    # down". Only the first deserves to count against the
                    # circuit breaker; the second should pause and retry the
                    # same video, so an ISP blip overnight costs waiting
                    # rather than a manual restart in the morning.
                    if not network_up() and network_retries < MAX_NETWORK_RETRIES:
                        network_retries += 1
                        progress.console.print(
                            f"  [yellow]offline[/yellow] {video.title[:42]} — waiting for network"
                        )
                        if wait_for_network(
                            on_wait=lambda m: progress.console.print(f"  [dim]network: {m}[/dim]")
                        ):
                            continue  # same video, nothing counted against it
                        progress.console.print("  [red]network never returned[/red]")

                    # One bad video must not kill a multi-hour run.
                    failures.append((video.title, str(exc)))
                    consecutive_failures += 1
                    progress.console.print(f"  [red]fail[/red] {video.title[:52]} — {exc}")

                    # Back-to-back failures with the network *up* means
                    # something systemic is wrong. Stop cleanly instead of
                    # ripping through the rest of the playlist failing
                    # instantly and reporting a "finished" run that did nothing.
                    if stop_after_failures and consecutive_failures >= stop_after_failures:
                        aborted = True
                        progress.console.print(
                            f"\n[bold red]{consecutive_failures} failures in a row — "
                            f"stopping.[/bold red] Re-run the same command once it's sorted: "
                            f"finished videos are cached and will be skipped."
                        )
                    break

            progress.advance(task)
            if aborted:
                break

    cached_now = len(cached_video_ids())
    console.print(
        f"\n[bold green]Indexed {indexed} chunks[/bold green] from {done} video(s). "
        f"{cached_now} transcript(s) now cached."
    )
    if skipped:
        console.print(f"[yellow]Skipped {skipped}[/yellow] video(s) with no cached transcript.")
    if failures:
        console.print(f"[bold red]{len(failures)} failure(s):[/bold red]")
        for title, err in failures:
            console.print(f"  • {title[:52]} — {err[:100]}")
    if aborted or failures:
        console.print(
            "\n[dim]Re-run the same command to continue — cached transcripts are skipped "
            "and upserts are idempotent, so nothing is redone or duplicated.[/dim]"
        )


# ------------------------------------------------------------------
# reindex
# ------------------------------------------------------------------
@app.command()
def reindex(
    replace: bool = typer.Option(
        False, "--replace", help="Delete each video's existing chunks first (needed if chunk settings changed)."
    ),
    transcripts: Path = typer.Option(
        None,
        "--transcripts",
        help="Read transcripts from this folder instead of ~/.ytrag/transcripts. "
        "Use the repo's bundled transcripts/ to build an index without a GPU.",
    ),
):
    """Re-chunk and re-embed from cached transcripts. Never re-transcribes.

    This is what makes changing your mind about the embedding model or chunk
    size cost minutes instead of hours — and it is how someone without a GPU
    builds the whole index from the transcripts shipped in the repo.
    """
    # Precedence matters. Your own live cache always wins over the copy
    # committed to the repo — that copy is a point-in-time snapshot and goes
    # stale the moment you transcribe anything new. The bundled folder is a
    # fallback for someone who cloned the repo and has no cache of their own.
    if transcripts:
        source = transcripts
    elif cached_video_ids():
        source = config.TRANSCRIPT_DIR
    else:
        source = _bundled_transcripts() or config.TRANSCRIPT_DIR

    video_ids = cached_video_ids(source)
    if not video_ids:
        console.print(
            f"[yellow]No transcripts in {source}.[/yellow] "
            "Run `ytrag ingest` first, or pass --transcripts."
        )
        raise typer.Exit(1)

    console.print(f"Rebuilding index from [bold]{len(video_ids)}[/bold] transcripts in {source}.")
    console.print(f"Embedding model: [cyan]{config.EMBED_MODEL}[/cyan]\n")

    total = 0
    with _progress() as progress:
        task = progress.add_task("Reindexing", total=len(video_ids))
        for video_id in video_ids:
            data = load_transcript(video_id, source)
            if data is None:
                progress.console.print(f"  [red]skip[/red] {video_id} — unreadable transcript")
                progress.advance(task)
                continue

            video = Video(
                video_id=video_id,
                title=data.get("title") or video_id,
                duration=int(data.get("duration") or 0),
            )
            progress.update(task, description=f"[cyan]{video.title[:48]}")

            if replace:
                delete_video(video_id)

            chunks = chunk_segments(video, segments_from_transcript(data))
            if chunks:
                upsert_chunks(chunks)
                total += len(chunks)
            progress.advance(task)

    console.print(f"\n[bold green]Reindexed {total} chunks.[/bold green]")


# ------------------------------------------------------------------
# ask / search
# ------------------------------------------------------------------
@app.command()
def ask(
    question: str = typer.Argument(..., help="Your question, in English or Hinglish."),
    top_k: int = typer.Option(config.TOP_K, "--top-k", "-k"),
    video: str = typer.Option("", "--video", help="Restrict to one video ID."),
):
    """Ask a question and get a grounded answer with clickable timestamps."""
    result = answer_question(question, top_k=top_k, video_id=video or None)

    style = "green" if result["grounded"] else "yellow"
    console.print(Panel(result["answer"], title="Answer", border_style=style))

    if not result["citations"]:
        console.print(
            f"[dim]No grounded sources (retrieved {result['retrieved']} chunk(s) "
            f"under distance {config.MAX_DISTANCE}).[/dim]"
        )
        return

    table = Table(title="Sources", show_lines=False)
    table.add_column("#", style="dim", width=3)
    table.add_column("Lecture")
    table.add_column("At", width=9)
    table.add_column("Jump")

    for i, c in enumerate(result["citations"], start=1):
        table.add_row(
            f"[{i}]",
            c["title"][:46],
            c["timestamp"],
            f"[link={c['url']}]▸ open[/link]",
        )
    console.print(table)


@app.command()
def search(
    question: str = typer.Argument(...),
    top_k: int = typer.Option(config.TOP_K, "--top-k", "-k"),
):
    """Retrieval only — see exactly what comes back, and at what distance."""
    hits = retrieve_only(question, top_k=top_k)
    if not hits:
        console.print("[yellow]Nothing retrieved. Is the collection populated?[/yellow]")
        return

    table = Table(title=f"Top {len(hits)} — cutoff is {config.MAX_DISTANCE}")
    table.add_column("Dist", width=6)
    table.add_column("Lecture")
    table.add_column("At", width=9)
    table.add_column("Text")

    for chunk, distance in hits:
        body = chunk.text.split("\n\n", 1)[-1]
        colour = "green" if distance <= config.MAX_DISTANCE else "red"
        table.add_row(
            f"[{colour}]{distance:.3f}[/{colour}]",
            chunk.video_title[:30],
            chunk.timestamp,
            body[:90].replace("\n", " ") + "…",
        )
    console.print(table)


# ------------------------------------------------------------------
# stats
# ------------------------------------------------------------------
@app.command()
def progress(
    playlist: str = typer.Option(
        "", "--playlist", "-p", help="Compare against this playlist's total length."
    ),
):
    """How far along is an ingest? Safe to run while one is going.

    Deliberately touches nothing heavy — no embedding model, no Qdrant, no
    GPU. It just reads the transcripts folder, so it cannot slow down or
    interfere with a run in flight.
    """
    ids = cached_video_ids()
    if not ids:
        console.print("[yellow]No transcripts yet.[/yellow]")
        return

    done_minutes = 0.0
    times = []
    for video_id in ids:
        path = transcript_path(video_id)
        times.append(path.stat().st_mtime)
        data = load_transcript(video_id)
        if data and data.get("segments"):
            done_minutes += data["segments"][-1]["end"] / 60.0

    console.print(f"Transcripts: [bold]{len(ids)}[/bold]")
    console.print(f"Audio done:  [bold]{done_minutes / 60:.1f}[/bold] hours")

    # Throughput from the last few transcripts, which reflects current speed
    # better than an average over the whole run.
    times.sort()
    recent = times[-6:]
    if len(recent) >= 2:
        span_min = (recent[-1] - recent[0]) / 60.0
        if span_min > 0:
            recent_audio = 0.0
            for video_id in ids:
                path = transcript_path(video_id)
                if path.stat().st_mtime >= recent[0] and path.stat().st_mtime != recent[0]:
                    data = load_transcript(video_id)
                    if data and data.get("segments"):
                        recent_audio += data["segments"][-1]["end"] / 60.0
            if recent_audio:
                speed = recent_audio / span_min
                console.print(f"Speed:       [bold]{speed:.1f}x[/bold] realtime")

                if playlist:
                    videos = list_playlist(playlist)
                    total_minutes = sum(v.duration for v in videos) / 60.0
                    pct = done_minutes / total_minutes * 100 if total_minutes else 0
                    remaining = max(0.0, total_minutes - done_minutes)
                    eta_hours = remaining / speed / 60 if speed else 0
                    console.print(
                        f"\n[bold]{len(ids)}/{len(videos)}[/bold] videos  •  "
                        f"[bold]{pct:.1f}%[/bold] of audio  •  "
                        f"ETA [bold]{eta_hours:.1f}h[/bold]"
                    )
                    bar_width = 40
                    filled = int(bar_width * pct / 100)
                    console.print(f"[green]{'█' * filled}[/green]{'░' * (bar_width - filled)}")

    newest = max(times)
    import time as _time

    idle_min = (_time.time() - newest) / 60
    colour = "green" if idle_min < 15 else "yellow" if idle_min < 40 else "red"
    console.print(
        f"\n[dim]Last transcript written [/dim][{colour}]{idle_min:.0f} min ago[/{colour}]"
        + ("[dim] — looks stalled?[/dim]" if idle_min > 40 else "")
    )


@app.command()
def stats():
    """What is actually in the index right now."""
    info = index_stats()
    transcripts = cached_video_ids()

    console.print(f"Collection:      [bold]{info['collection']}[/bold]")
    console.print(f"Embedding model: [cyan]{config.EMBED_MODEL}[/cyan]")
    console.print(f"Transcripts:     {len(transcripts)} cached in {config.TRANSCRIPT_DIR}")

    if not info["exists"]:
        console.print("[yellow]Collection does not exist yet.[/yellow]")
        return

    console.print(f"Chunks:          [bold]{info['chunks']}[/bold] ({info['dim']}-dim)\n")

    table = Table(title="Per video")
    table.add_column("Video ID", style="dim")
    table.add_column("Lecture")
    table.add_column("Chunks", justify="right")
    for video_id, entry in sorted(info["videos"].items(), key=lambda kv: -kv[1]["chunks"]):
        table.add_row(video_id, entry["title"][:52], str(entry["chunks"]))
    console.print(table)


# ------------------------------------------------------------------
# eval
# ------------------------------------------------------------------
@app.command(name="eval")
def eval_cmd(
    path: Path = typer.Option(DEFAULT_GOLDEN, "--path", help="Golden set JSON."),
    k: int = typer.Option(5, "--k", help="Retrieval depth to score at."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show what each miss returned."),
):
    """Score retrieval against the golden set."""
    report = run_eval(path, k=k)
    if report["n"] == 0:
        console.print(f"[yellow]No entries in {path}. Fill it in — see the README.[/yellow]")
        raise typer.Exit(1)

    rate = report[f"hit_rate_at_{k}"]
    colour = "green" if rate >= 0.8 else "yellow" if rate >= 0.6 else "red"
    console.print(
        Panel(
            f"[{colour}]hit_rate@{k} = {rate:.2%}[/{colour}]  ({report['n']} questions)\n"
            f"retrieval: {report.get('retrieval_hit_rate', 0):.2%}   "
            f"video-only: {report.get('video_hit_rate', 0):.2%}   "
            f"refusal: {report.get('refusal_rate', 0):.2%}\n"
            f"[dim]MAX_DISTANCE = {report['max_distance']}[/dim]",
            title="Golden set",
        )
    )

    if not report["misses"]:
        console.print("[green]No misses.[/green]")
        return

    console.print(f"[bold red]{len(report['misses'])} miss(es):[/bold red]")
    for miss in report["misses"]:
        console.print(f"  • {miss['q']}")
        if miss["kind"] == "retrieval":
            around = miss["expect_around_sec"]
            expected_at = format_timestamp(around) if around is not None else "anywhere"
            console.print(
                f"    expected {miss['expected']} @ {expected_at} — "
                f"video in top-{k}: {'yes' if miss['video_hit'] else 'no'}"
            )
            if verbose:
                for got in miss["got"]:
                    console.print(
                        f"      got {got['video_id']} @ {got['timestamp']} "
                        f"(d={got['distance']}) {got['title'][:34]}"
                    )
        else:
            console.print(f"    expected a refusal, got: {miss['answer'][:110]}")


# ------------------------------------------------------------------
# langtest — §6.0, run this before ingesting anything
# ------------------------------------------------------------------
@app.command()
def langtest(
    url: str = typer.Argument(..., help="A single lecture URL."),
    seconds: int = typer.Option(180, "--seconds", help="How much of the lecture to transcribe."),
    languages: str = typer.Option("en,hi", "--languages", help="Comma-separated language codes."),
):
    """Transcribe one lecture in two languages and print both, side by side.

    The lectures are Hinglish. language="hi" gives Devanagari; language="en"
    gives romanised/translated output. Student queries will be romanised
    Hinglish or English, so these two produce very different retrieval
    behaviour. Read a few minutes of each and check what happens to the
    technical terms specifically — memoization, adjacency list, time
    complexity, subproblem, DP table. Whichever keeps those clean, wins.

    This decision gets baked into hours of compute afterwards, so make it on
    evidence rather than on expectation.
    """
    videos = list_playlist(url)
    if not videos:
        console.print("[red]Could not resolve that URL to a video.[/red]")
        raise typer.Exit(1)
    video = videos[0]

    console.print(f"[bold]{video.title}[/bold]")
    console.print(f"Transcribing the first {seconds}s in: {languages}\n")

    audio_path = download_audio(video)
    out_dir = config.ROOT / "langtest"
    out_dir.mkdir(parents=True, exist_ok=True)

    for lang in [code.strip() for code in languages.split(",") if code.strip()]:
        console.print(f"[bold cyan]── language={lang} ──[/bold cyan]")
        raw, _ = run_whisper(str(audio_path), lang)

        lines = []
        for segment in raw:
            if segment.start > seconds:
                break
            text = segment.text.strip()
            if not text:
                continue
            lines.append({"start": segment.start, "end": segment.end, "text": text})
            console.print(f"[dim]{format_timestamp(int(segment.start))}[/dim] {text}")

        out = out_dir / f"{video.video_id}.{lang}.json"
        with open(out, "w", encoding="utf-8") as f:
            json.dump(lines, f, ensure_ascii=False, indent=1)
        console.print(f"[dim]saved -> {out}[/dim]\n")

    # The audio stays put — you will want it for a second pass.
    console.print(
        f"[dim]Audio kept at {audio_path}. "
        f"Set YTRAG_WHISPER_LANG to whichever won, then run `ytrag ingest`.[/dim]"
    )


# ------------------------------------------------------------------
# housekeeping
# ------------------------------------------------------------------
@app.command()
def preflight(playlist: str = typer.Option("", "--playlist", "-p", help="Also check this URL lists.")):
    """Exercise every code path a long ingest depends on, in about a minute.

    Written after an 8-hour run died ten seconds in on a missing import. The
    point is that each check actually *calls* the thing rather than asserting
    it looks importable.
    """
    ok = True

    def check(name: str, fn):
        nonlocal ok
        try:
            detail = fn()
            console.print(f"  [green]pass[/green] {name}" + (f" — {detail}" if detail else ""))
            return True
        except Exception as exc:
            ok = False
            console.print(f"  [red]FAIL[/red] {name} — {type(exc).__name__}: {str(exc)[:100]}")
            return False

    console.print("[bold]Config[/bold]")
    check("GROQ_API_KEY set", lambda: "yes" if config.GROQ_API_KEY else _raise("missing"))
    check("QDRANT_URL set", lambda: "yes" if config.QDRANT_URL else _raise("missing"))
    check(
        "whisper settings",
        lambda: f"{config.WHISPER_MODEL} lang={config.WHISPER_LANG} "
        f"batch={config.WHISPER_BATCH} beam={config.WHISPER_BEAM}",
    )

    console.print("\n[bold]Vector store[/bold]")
    check("qdrant reachable", lambda: f"{len(get_client().get_collections().collections)} collections")
    check("embedder loads", lambda: f"{config.EMBED_MODEL} ({get_embedder().dim}-dim)")
    check("collection ready", lambda: ensure_collection())
    check("query round-trip", lambda: f"{len(retrieve_only('preflight probe', top_k=1))} hit(s)")

    console.print("\n[bold]Transcription[/bold]")
    # These two are the checks that would have caught the missing import: they
    # call the real functions rather than merely importing the module.
    check("whisper model loads", lambda: type(get_model()).__name__)
    check(
        "run_whisper path executes",
        lambda: _probe_run_whisper(),
    )

    console.print("\n[bold]Network[/bold]")
    if playlist:
        check("playlist lists", lambda: f"{len(list_playlist(playlist))} videos")

    console.print("\n[bold]LLM (optional - search works without it)[/bold]")
    check(f"{config.LLM_BACKEND} responds", _probe_llm)

    if ok:
        console.print("\n[bold green]All preflight checks passed.[/bold green]")
    else:
        console.print("\n[bold red]Preflight failed — fix the above before a long run.[/bold red]")
        raise typer.Exit(1)


def _raise(message: str):
    raise RuntimeError(message)


def _probe_run_whisper() -> str:
    """Drive run_whisper far enough to prove every name in it resolves.

    Pointed at a path that cannot exist, so the only acceptable failure is a
    file error. A NameError or a bad faster-whisper call surfaces here instead
    of eight hours into an unattended run.
    """
    try:
        segments, _ = run_whisper("__preflight_no_such_file__.wav", config.WHISPER_LANG)
        list(segments)
    except (NameError, AttributeError, TypeError, ImportError) as exc:
        raise RuntimeError(f"code path broken: {type(exc).__name__}: {exc}") from exc
    except Exception:
        pass  # file-not-found and friends are the expected outcome
    return "reached faster-whisper cleanly"


def _probe_llm() -> str:
    """Exercise whichever backend is configured, not a hardcoded one."""
    from ytrag.answer import _chat

    if config.LLM_BACKEND == "none":
        return "disabled (retrieval still works)"
    reply = _chat("Reply with exactly: ok", "ok?")
    return f"{config.LLM_BACKEND}: {reply.strip()[:12]}"


def _bundled_vectors() -> Path | None:
    """The prebuilt index committed to the repo, if there is one."""
    f = Path(__file__).resolve().parent.parent / "index" / "vectors.npz"
    return f if f.exists() else None


@app.command()
def export_vectors_cmd(
    dest: Path = typer.Option(None, "--out", help="Defaults to ./index/vectors.npz"),
):
    """Save the built index so others can load it without embedding anything."""
    from ytrag.index import export_vectors

    target = dest or (Path(__file__).resolve().parent.parent / "index" / "vectors.npz")
    info = export_vectors(target)
    console.print(
        f"Exported [bold]{info['count']}[/bold] vectors "
        f"({info['mb']:.1f} MB) to {target}"
    )
    console.print("[dim]Commit this. Anyone who clones can then run `ytrag load`.[/dim]")


@app.command()
def load(
    path: Path = typer.Option(None, "--path", help="Defaults to the repo's index/vectors.npz"),
):
    """Load the prebuilt index. Seconds, instead of minutes of embedding."""
    from ytrag.index import import_vectors

    source = path or _bundled_vectors()
    if source is None:
        console.print(
            "[yellow]No prebuilt index found.[/yellow] Run `ytrag reindex` to build one."
        )
        raise typer.Exit(1)

    console.print(f"Loading prebuilt index from {source} …")
    info = import_vectors(source)
    console.print(
        f"[bold green]Loaded {info['count']} chunks[/bold green] "
        f"(embedded with {info['model']})."
    )
    console.print("[dim]Now run `ytrag serve`.[/dim]")


def _bundled_transcripts() -> Path | None:
    """The repo's own transcripts/ folder, if it has anything in it.

    Lets someone clone the repo and build the index with no GPU and no
    downloads — transcripts are ~1.4 KB per minute of video, so a 68-hour
    playlist ships in about 6 MB of JSON.
    """
    folder = Path(__file__).resolve().parent.parent / "transcripts"
    if folder.is_dir() and any(folder.glob("*.json")):
        return folder
    return None


@app.command()
def export_transcripts(
    dest: Path = typer.Argument(None, help="Where to write them. Defaults to ./transcripts."),
):
    """Copy cached transcripts into the repo so they can be committed and shared.

    This is the artifact worth distributing. It costs GPU-hours to produce and
    nothing to consume — anyone with it can rebuild the entire index in minutes
    on a laptop.
    """
    import shutil

    target = dest or (Path(__file__).resolve().parent.parent / "transcripts")
    target.mkdir(parents=True, exist_ok=True)

    ids = cached_video_ids()
    if not ids:
        console.print("[yellow]Nothing to export — no cached transcripts.[/yellow]")
        raise typer.Exit(1)

    total_bytes = 0
    for video_id in ids:
        src = transcript_path(video_id)
        shutil.copy2(src, target / src.name)
        total_bytes += src.stat().st_size

    console.print(
        f"Exported [bold]{len(ids)}[/bold] transcripts "
        f"({total_bytes / 1024 / 1024:.1f} MB) to {target}"
    )
    console.print("[dim]Commit these. Anyone who clones can then run `ytrag reindex`.[/dim]")
    console.print(
        "[dim]This is a snapshot — re-run it after transcribing anything new. "
        "Your own commands always use the live cache, never this copy.[/dim]"
    )


@app.command()
def clean_audio():
    """Delete every downloaded audio file. Transcripts are untouched."""
    count = 0
    for path in config.AUDIO_DIR.glob("*"):
        if path.is_file():
            path.unlink(missing_ok=True)
            count += 1
    console.print(f"Deleted {count} audio file(s) from {config.AUDIO_DIR}.")


@app.command()
def serve(
    host: str = typer.Option("127.0.0.1", "--host"),
    port: int = typer.Option(8000, "--port"),
    reload: bool = typer.Option(False, "--reload"),
):
    """Run the FastAPI app and the web UI."""
    import os
    import sys

    import uvicorn

    # `api/` is not part of the installed wheel (only `ytrag` is), so make the
    # project root importable rather than relying on the cwd.
    project_root = Path(__file__).resolve().parent.parent
    if not (project_root / "api" / "main.py").exists():
        console.print(f"[red]Can't find api/main.py under {project_root}.[/red]")
        raise typer.Exit(1)

    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    # Check the port before loading a 90MB model and reporting "startup
    # complete", only to fail on bind afterwards. uvicorn's own message arrives
    # after the success line and reads like the app crashed for no reason.
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.settimeout(1)
        if probe.connect_ex((host, port)) == 0:
            console.print(
                f"[bold red]Port {port} is already in use.[/bold red]\n"
                f"Something is already listening on {host}:{port} — most likely "
                f"another `ytrag serve` you started earlier.\n\n"
                f"Either stop that one (Ctrl-C in its window), or use another "
                f"port here:\n  [cyan]uv run ytrag serve --port {port + 1}[/cyan]\n\n"
                f"[dim]To find it on Windows:  netstat -ano | findstr :{port}[/dim]"
            )
            raise typer.Exit(1)

    console.print("[dim]Starting… the embedding model loads first (a few seconds).[/dim]")
    console.print(f"[bold green]http://{host}:{port}[/bold green]  [dim](Ctrl-C to stop)[/dim]")

    if reload:
        # --reload needs an import string, and the reloader spawns a fresh
        # process that won't inherit our sys.path edit.
        os.chdir(project_root)
        uvicorn.run("api.main:app", host=host, port=port, reload=True)
    else:
        from api.main import app as fastapi_app

        uvicorn.run(fastapi_app, host=host, port=port)


if __name__ == "__main__":
    app()
