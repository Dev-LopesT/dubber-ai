from enum import Enum


class JobStatus(str, Enum):
    CREATED = "created"
    UPLOADED = "uploaded"
    QUEUED = "queued"
    TRANSCRIBING = "transcribing"
    TRANSCRIBED = "transcribed"
    ERROR = "error"
