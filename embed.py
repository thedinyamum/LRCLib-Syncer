from pathlib import Path

from mutagen import File
from mutagen.flac import FLAC
from mutagen.mp4 import MP4
from mutagen.id3 import ID3, USLT
from mutagen.oggvorbis import OggVorbis
from mutagen.oggopus import OggOpus
from mutagen.mp3 import MP3


def embed(path, lyrics):
    """
    Embed lyrics into an audio file.

    Returns True on success.
    """

    try:
        audio = File(path)

        if audio is None:
            return False

        # ---------- FLAC ----------
        if isinstance(audio, FLAC):
            audio["LYRICS"] = [lyrics]
            audio.save()
            return True

        # ---------- M4A ----------
        elif isinstance(audio, MP4):
            audio["©lyr"] = [lyrics]
            audio.save()
            return True

        # ---------- MP3 ----------
        elif isinstance(audio, MP3):
            if audio.tags is None:
                audio.add_tags()

            # Remove existing lyrics
            audio.tags.delall("USLT")

            audio.tags.add(
                USLT(
                    encoding=3,
                    lang="eng",
                    desc="",
                    text=lyrics,
                )
            )

            audio.save()
            return True

        # ---------- OGG ----------
        elif isinstance(audio, OggVorbis):
            audio["LYRICS"] = [lyrics]
            audio.save()
            return True

        # ---------- OPUS ----------
        elif isinstance(audio, OggOpus):
            audio["LYRICS"] = [lyrics]
            audio.save()
            return True

    except Exception:
        return False

    return False
