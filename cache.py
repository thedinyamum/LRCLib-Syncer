import json
from pathlib import Path
from threading import Lock

CACHE_FILE = Path(".lyrics_cache.json")


class LyricsCache:
    def __init__(self):
        self.lock = Lock()
        if CACHE_FILE.exists():
            self.data = json.loads(CACHE_FILE.read_text("utf-8"))
        else:
            self.data = {}

    def key(self, artist, title):
        return f"{artist.lower().strip()}|{title.lower().strip()}"

    def get(self, artist, title):
        with self.lock:
            return self.data.get(self.key(artist, title))

    def put(self, artist, title, value):
        with self.lock:
            self.data[self.key(artist, title)] = value

    def save(self):
        with self.lock:
            CACHE_FILE.write_text(
                json.dumps(
                    self.data,
                    indent=2,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
        )
