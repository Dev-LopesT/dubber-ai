from faster_whisper import WhisperModel


# M1-friendly defaults
# - "base" is fast and decent quality
# - compute_type="int8" is a good balance on Apple Silicon
_model = WhisperModel("base", compute_type="int8")


def transcribe_file(audio_path: str) -> str:
    segments, _info = _model.transcribe(audio_path)

    parts: list[str] = []
    for segment in segments:
        parts.append(segment.text.strip())

    return " ".join([p for p in parts if p]).strip()