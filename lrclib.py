import time

from search import search
from chooser import choose


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
