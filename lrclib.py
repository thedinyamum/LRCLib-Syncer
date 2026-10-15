import re
import time
from urllib.parse import urlparse

import requests

from search import search
from chooser import choose

TRACK_API = "https://lrclib.net/api/get"


def fetch_track_url(url):
    """
    Fetch one exact LRCLIB track by URL, bypassing search and match scoring.

    Accepts public track URLs such as https://lrclib.net/tracks/39180465.
    """
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.netloc.lower() not in {
        "lrclib.net", "www.lrclib.net"
    }:
        raise ValueError("Expected an https://lrclib.net/tracks/<id> URL.")

    match = re.fullmatch(r"/tracks/(\d+)/?", parsed.path)
    if not match:
        raise ValueError("Expected a track URL like https://lrclib.net/tracks/39180465.")

    track_id = match.group(1)
    response = requests.get(
        f"{TRACK_API}/{track_id}",
        timeout=15,
        headers={"User-Agent": "LRCLib-Syncer/1.0 (https://github.com/thedinyamum/LRCLib-Syncer)"},
    )
    response.raise_for_status()
    item = response.json()

    lyrics = item.get("syncedLyrics") or item.get("plainLyrics")
    if not lyrics:
        return None

    return {
        "title": item.get("trackName"),
        "artist": item.get("artistName"),
        "album": item.get("albumName"),
        "duration": item.get("duration"),
        "lyrics": lyrics,
        "synced": bool(item.get("syncedLyrics")),
        "instrumental": item.get("instrumental", False),
        "lrclib_id": item.get("id"),
    }


def fetch(title, artist, duration=None, album=None, interactive=False):
    strategies = [
        {"title": title, "artist": artist, "album": album, "duration": duration},
        {"title": title, "artist": artist, "duration": duration},
        {"title": title, "artist": artist},
        {"title": title, "album": album},
    ]

    if album:
        strategies.append({
            "album": album,
            "expected_title": title,
        })

    for attempt in range(3):
        try:
            for query in strategies:
                candidates = search(**query)

                if candidates:
                    return choose(
                        candidates,
                        interactive=interactive,
                    )

            return None

        except Exception:
            if attempt == 2:
                return None

            time.sleep(attempt + 1)
