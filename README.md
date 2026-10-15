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
