import requests

from score import score
from normalize import normalize

API = "https://lrclib.net/api/search"


def search(title=None, artist=None, duration=None, album=None, expected_title=None):
    params = {
        k: v
        for k, v in {
            "track_name": title,
            "artist_name": artist,
            "album_name": album,
        }.items()
        if v
    }

    r = requests.get(API, params=params, timeout=15)
    r.raise_for_status()

    candidates = []

    album_only = album is not None and title is None and artist is None

    for item in r.json():
        if album_only and expected_title:
            if normalize(item["trackName"]) != normalize(expected_title):
                continue

        lyrics = item.get("syncedLyrics") or item.get("plainLyrics")

        candidate = {
            "title": item["trackName"],
            "artist": item["artistName"],
            "album": item.get("albumName"),
            "duration": item.get("duration"),
            "lyrics": lyrics,
            "synced": bool(item.get("syncedLyrics")),
            "instrumental": item.get("instrumental", False),
        }

        candidate["score"] = score(
            {
                "title": expected_title or title,
                "artist": artist,
                "album": album,
                "duration": duration,
            },
            candidate,
        )

        candidates.append(candidate)

    candidates.sort(key=lambda x: x["score"], reverse=True)
    return candidates
