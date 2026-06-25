#  transcriber.py
from faster_whisper import WhisperModel
import os

WHISPER_MODEL = os.getenv(
    "WHISPER_MODEL",
    "base"
)

_model = None


def load_model():

    global _model

    if _model is None:

        print(
            f"Loading {WHISPER_MODEL}"
        )

        _model = WhisperModel(
            WHISPER_MODEL,
            device="cpu",
            compute_type="int8"
        )

    return _model


def transcribe_chunk_whisper(
    chunk_path,
    language=None
):

    model = load_model()

    segments, info = model.transcribe(
        chunk_path,
        beam_size=3,
        vad_filter=True,
    )

    text = []

    for s in segments:

        if s.text:

            text.append(
                s.text.strip()
            )

    return " ".join(text)


def transcribe_all(
    chunks,
    language="english"
):

    transcript = []

    for chunk in chunks:

        try:

            result = (
                transcribe_chunk_whisper(
                    chunk
                )
            )

            if result.strip():

                transcript.append(
                    result
                )

        except Exception as e:

            print(
                f"Chunk failed: {e}"
            )

    final = "\n".join(
        transcript
    )

    print(
        "Transcript length:",
        len(final)
    )

    return final