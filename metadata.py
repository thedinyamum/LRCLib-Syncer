from mutagen import File


def tag(audio, *names):
    for name in names:
        if name in audio:
            value = audio[name]
            if isinstance(value, list):
                return str(value[0]).strip()
            return str(value).strip()
    return None


def read(path):
    audio = File(path, easy=True)

    if audio is None:
        return None

    return {
        "audio": audio,
        "title": tag(audio, "title"),
        "artist": tag(audio, "artist", "albumartist"),
        "album": tag(audio, "album"),
        "duration": int(audio.info.length),
    }
