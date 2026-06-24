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


def convert_to_wav(path):

    if AudioSegment is None:
        raise RuntimeError(
            "Audio conversion unavailable on deployment. Upload WAV files or use YouTube URL."
        )

    output = (
        os.path.splitext(path)[0]
        + "_converted.wav"
    )

    audio = AudioSegment.from_file(path)

    audio = (
        audio
        .set_channels(1)
        .set_frame_rate(16000)
    )

    audio.export(
        output,
        format="wav"
    )

    return output


def chunk_audio(
    wav,
    minutes=DEFAULT_CHUNK_MINUTES
):
    if AudioSegment is None:
     raise RuntimeError(
        "Audio processing unavailable in cloud deployment."
     )

    audio = AudioSegment.from_wav(
        wav
    )

    ms = int(
        minutes
        * 60
        * 1000
    )

    chunks = []

    base = os.path.abspath(
        wav
    )

    for i, start in enumerate(
        range(
            0,
            len(audio),
            ms
        )
    ):

        out = (
            f"{base}_chunk_{i}.wav"
        )

        audio[
            start:
            start+ms
        ].export(
            out,
            format="wav"
        )

        chunks.append(out)

    return chunks


def process_input(source):

    if source.startswith("http"):

        print(
            "Downloading..."
        )

        wav = (
            download_youtube_audio(
                source
            )
        )

    else:

        wav = convert_to_wav(
            source
        )

    print(
        "Creating chunks..."
    )

    return chunk_audio(
        wav
    )

def cleanup(files):
    for file in files:
        try:
            os.remove(file)
        except:
            pass

        