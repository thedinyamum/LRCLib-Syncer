# LRCLib Syncer
Download Lyrics embedded and LRC files for your music from LRClib.net

## Requirements

- FFMPEG
- Python 3.10+
- mutagen
- tqdm
- Requests

## Installation

- clone/download the repo
- `pip install ffmpeg mutagen tqdm`
- cd `<YOUR_PATH_TO>/lrclib-syncer`

## How to use?

- Open Terminal <sub><sub><sub>cancer</sub></sub></sub>
- Type: `python lyrics_fetch.py Music_Folder_Path`
- Done, your lyrics are embedded!
- All known failures/missing lyrics are logged in `lyrics_missing.txt`.
- All known instrumentals are logged in `instrumentals.txt`.

## Force a specific LRCLIB track

If search does not find a track but you have its LRCLIB page URL, fetch that exact track directly:

```bash
python lyrics_fetch.py --force-url "https://lrclib.net/tracks/39180465" "$HOME/Music/Various Artists/Grand Theft Auto VI_ The Album/07 Cardi B - Don't Chart.flac"
```

This bypasses search and match selection, then writes a `.lrc` sidecar next to the audio file and attempts to embed the lyrics into the audio file. The URL must be a track page in the form `https://lrclib.net/tracks/<id>`.
