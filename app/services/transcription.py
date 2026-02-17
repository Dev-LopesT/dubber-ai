from faster_whisper import WhisperModel


def _get_model() -> WhisperModel:
    # Lazy init prevents heavy model load at import time and works better with
    # Celery prefork workers.
    if not hasattr(_get_model, "_model"):
        _get_model._model = WhisperModel("base", compute_type="int8")
    return _get_model._model  # type: ignore[attr-defined]


def transcribe_file(audio_path: str) -> str:
    model = _get_model()
    segments, _info = model.transcribe(audio_path)

    parts: list[str] = []
    for segment in segments:
        parts.append(segment.text.strip())

    return " ".join([p for p in parts if p]).strip()
