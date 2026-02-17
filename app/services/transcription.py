from faster_whisper import WhisperModel

_model: WhisperModel | None = None


def _get_model() -> WhisperModel:
    global _model
    # Lazy init prevents heavy model load at import time and works better with
    # Celery prefork workers.
    if _model is None:
        _model = WhisperModel("base", compute_type="int8")
    return _model


def transcribe_file(audio_path: str) -> str:
    model = _get_model()
    segments, _info = model.transcribe(audio_path)

    parts: list[str] = []
    for segment in segments:
        parts.append(segment.text.strip())

    return " ".join([p for p in parts if p]).strip()
