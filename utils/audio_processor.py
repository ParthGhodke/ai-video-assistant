#  audio_processor.py

import os
import yt_dlp
try:
    from pydub import AudioSegment
except ModuleNotFoundError:
    AudioSegment = None

DOWNLOAD_DIR = "downloads"

os.makedirs(
    DOWNLOAD_DIR,
    exist_ok=True
)

DEFAULT_CHUNK_MINUTES = float(
    os.getenv(
        "CHUNK_MINUTES",
        "5"
    )
)


def download_youtube_audio(url):

    output = os.path.join(
        DOWNLOAD_DIR,
        "%(title)s.%(ext)s"
    )

    ydl_opts = {
    "format": "bestaudio/best",

    "outtmpl": output,

    "quiet": True,

    "nocheckcertificate": True,

    "extract_flat": False,

    "http_headers": {
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    },

    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "wav",
        }
    ],
}

    with yt_dlp.YoutubeDL(
        ydl_opts
    ) as ydl:

        info = ydl.extract_info(
        url,
       download=False
   )

    video_url = info["webpage_url"]

    info = ydl.extract_info(
    video_url,
    download=True
)

    file = ydl.prepare_filename(
            info
        )

    return os.path.splitext(
        file
    )[0] + ".wav"


import subprocess


def convert_to_wav(path):

    ext = os.path.splitext(path)[1].lower()

    if ext == ".wav":
        return path

    output = (
        os.path.splitext(path)[0]
        + "_converted.wav"
    )

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        path,
        "-ac",
        "1",
        "-ar",
        "16000",
        output,
    ]

    subprocess.run(
        cmd,
        check=True
    )

    return output


import subprocess
import math


def chunk_audio(
    wav,
    minutes=DEFAULT_CHUNK_MINUTES
):

    duration_cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        wav,
    ]

    duration = float(
        subprocess.check_output(
            duration_cmd
        )
        .decode()
        .strip()
    )

    chunk_seconds = (
        minutes * 60
    )

    chunks = []

    total = math.ceil(
        duration / chunk_seconds
    )

    base = os.path.splitext(
        wav
    )[0]

    for i in range(total):

        start = i * chunk_seconds

        out = (
            f"{base}_chunk_{i}.wav"
        )

        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            wav,
            "-ss",
            str(start),
            "-t",
            str(chunk_seconds),
            out,
        ]

        subprocess.run(
            cmd,
            check=True
        )

        chunks.append(out)

    return chunks

def process_input(source):

    # Uploaded file from Streamlit
    if hasattr(source, "name"):

        temp = os.path.join(
            DOWNLOAD_DIR,
            source.name
        )

        with open(temp, "wb") as f:
            f.write(source.getbuffer())

        wav = convert_to_wav(temp)

    # YouTube URL
    elif isinstance(source, str) and source.startswith("http"):

        print("Downloading...")

        wav = download_youtube_audio(
            source
        )

    # Local path
    else:

        wav = convert_to_wav(
            source
        )

    print("Creating chunks...")

    return chunk_audio(wav)

def cleanup(files):
    for file in files:
        try:
            os.remove(file)
        except:
            pass

        