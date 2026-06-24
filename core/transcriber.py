#  transcriber.py

from faster_whisper import WhisperModel
import os

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")

_model = None


def load_model():
    global _model

    if _model is None:
        print(f"Loading Faster Whisper ({WHISPER_MODEL})...")

        _model = WhisperModel(
            WHISPER_MODEL,
            device="cpu",
            compute_type="int8"
        )

        print("Model loaded.")

    return _model


def transcribe_chunk_whisper(chunk_path, language):

    model = load_model()

    print(f"Processing: {chunk_path}")

    segments, info = model.transcribe(
     chunk_path,
     language="en" if language=="english" else "hi",
     task="translate"
)
    text = " ".join(
        segment.text
        for segment in segments
    )

    return text


def transcribe_all(chunks, language="hinglish"):

    transcript = []

    for i, chunk in enumerate(chunks):

        print(
            f"Chunk {i+1}/{len(chunks)}"
        )

        try:
            text = transcribe_chunk_whisper(chunk)

            transcript.append(text)

        except Exception as e:

            print(f"Error: {e}")

    return "\n".join(transcript)