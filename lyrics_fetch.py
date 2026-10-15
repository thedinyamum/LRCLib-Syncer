#!/usr/bin/env python3

from pathlib import Path
import argparse
from threading import Lock, Semaphore

import requests

from metadata import read
from lrclib import fetch, fetch_track_url
from normalize import normalize
from cache import LyricsCache
from embed import embed
from worker import process_batch
from instrumental import is_instrumental

AUDIO_EXTS = {
    ".flac", ".mp3", ".m4a", ".aac",
    ".ogg", ".opus", ".wav"
}

cache = LyricsCache()

stats_lock = Lock()
missing_lock = Lock()
instrumentals_lock = Lock()
network_limit = Semaphore(4)


def process(path, missing, instrumentals, stats, interactive=False,):
    info = read(path)

    if info is None:
        return

    title = normalize(info["title"])
    artist = normalize(info["artist"])
    album = normalize(info["album"])
    duration = info["duration"]

    if not title or not artist:
        with missing_lock:
            missing.append(f"{path} (missing metadata)")
        with stats_lock:
            stats["missing"] += 1
        return

    result = cache.get(artist, title)

    if result is not None:
        with stats_lock:
            stats["cache_hits"] += 1
    else:
        with network_limit:
            result = fetch(
                title=title,
                artist=artist,
                album=album,
                duration=duration,
                interactive=interactive,
            )

        if result is not None:
            cache.put(artist, title, result)

    if result is None:
        with missing_lock:
            missing.append(f"{artist} - {title}")
        with stats_lock:
            stats["missing"] += 1
        return

    if is_instrumental(result):
        with instrumentals_lock:
            instrumentals.append(f"{artist} - {title}")
        with stats_lock:
            stats["instrumental"] += 1
        return

    lyrics = result["lyrics"]
    path.with_suffix(".lrc").write_text(lyrics, encoding="utf-8")

    if embed(path, lyrics):
        with stats_lock:
            stats["embedded"] += 1

    with stats_lock:
        stats["downloaded"] += 1
        if result["synced"]:
            stats["synced"] += 1
        else:
            stats["plain"] += 1


def write_result(path, result):
    """Write a fetched result to an LRC sidecar and the audio file."""
    if result is None:
        print("No lyrics found at that LRCLIB track.")
        return False

    if result.get("instrumental"):
        print("LRCLIB marks this track as instrumental; no lyrics written.")
        return False

    lyrics = result["lyrics"]
    lrc_path = path.with_suffix(".lrc")
    lrc_path.write_text(lyrics, encoding="utf-8")

    if embed(path, lyrics):
        print("✓ Embedded lyrics")
    else:
        print("⚠ Could not embed lyrics into this format; saved the .lrc file.")

    print(f"✓ Wrote {lrc_path.name}")
    return True


def scan(folder, interactive=False):
    files = [
        p for p in Path(folder).rglob("*")
        if p.suffix.lower() in AUDIO_EXTS
    ]

    missing = []
    instrumentals = []

    stats = {
        "downloaded": 0,
        "cache_hits": 0,
        "synced": 0,
        "plain": 0,
        "missing": 0,
        "instrumental": 0,
        "embedded": 0,
    }

    process_batch(
        files,
        process,
        missing,
        instrumentals,
        stats,
        interactive=interactive,
    )

    cache.save()

    if missing:
        Path("lyrics_missing.txt").write_text(
            "\n".join(missing),
            encoding="utf-8"
        )

    if instrumentals:
        Path("instrumentals.txt").write_text(
            "\n".join(instrumentals),
            encoding="utf-8",
        )

    print("\nFinished!\n")
    print(f"Processed : {len(files)}")
    print(f"Downloaded: {stats['downloaded']}")
    print(f"Cache hits: {stats['cache_hits']}")
    print(f"Synced    : {stats['synced']}")
    print(f"Plain     : {stats['plain']}")
    print(f"Embedded  : {stats['embedded']}")
    print(f"Instrumental: {stats['instrumental']}")
    print(f"Missing   : {stats['missing']}")


def main():
    parser = argparse.ArgumentParser(
        description="Download lyrics from LRCLIB."
    )

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        "folder",
        nargs="?",
        help="Music folder to scan"
    )

    group.add_argument(
        "--alt-search",
        nargs=3,
        metavar=("TITLE", "ARTIST", "FILE"),
        help="Search lyrics for one file using a custom title and artist."
    )

    group.add_argument(
        "--force-url",
        nargs=2,
        metavar=("LRCLIB_URL", "FILE"),
        help=(
            "Fetch an exact LRCLIB track URL (for example "
            "https://lrclib.net/tracks/39180465) and write its lyrics "
            "to the specified audio file, bypassing search."
        ),
    )

    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Ask before choosing ambiguous matches."
    )

    args = parser.parse_args()

    if args.force_url:
        url, filename = args.force_url
        path = Path(filename).expanduser().resolve()

        if not path.is_file():
            parser.error(f"File does not exist: {path}")

        info = read(path)
        if info is None:
            parser.error("Unsupported audio file.")

        try:
            with network_limit:
                result = fetch_track_url(url)
        except (ValueError, requests.RequestException) as exc:
            parser.error(f"Could not fetch LRCLIB track: {exc}")

        if write_result(path, result):
            file_title = normalize(info["title"])
            file_artist = normalize(info["artist"])
            if file_title and file_artist:
                cache.put(file_artist, file_title, result)
                cache.save()

            missing_file = Path("lyrics_missing.txt")
            if missing_file.exists() and file_title and file_artist:
                target = f"{file_artist} - {file_title}"
                lines = [
                    line for line in missing_file.read_text(encoding="utf-8").splitlines()
                    if normalize(line) != normalize(target)
                ]
                missing_file.write_text("\n".join(lines), encoding="utf-8")

    elif args.alt_search:
        title, artist, filename = args.alt_search
        path = Path(filename).expanduser().resolve()

        if not path.is_file():
            parser.error(f"File does not exist: {path}")

        info = read(path)
        if info is None:
            parser.error("Unsupported audio file.")

        with network_limit:
            result = fetch(
                title=normalize(title),
                artist=normalize(artist),
                album=normalize(info["album"]),
                duration=info["duration"],
                interactive=args.interactive,
            )

        if write_result(path, result):
            file_title = normalize(info["title"])
            file_artist = normalize(info["artist"])
            if file_title and file_artist:
                cache.put(file_artist, file_title, result)
                cache.save()

            missing_file = Path("lyrics_missing.txt")
            if missing_file.exists():
                target = f"{file_artist} - {file_title}"
                lines = [
                    line for line in missing_file.read_text(encoding="utf-8").splitlines()
                    if normalize(line) != normalize(target)
                ]
                missing_file.write_text("\n".join(lines), encoding="utf-8")

    else:
        scan(args.folder, interactive=args.interactive)


if __name__ == "__main__":
    main()
