from datetime import datetime
from sqlmodel import Session
from app.models import Job
from app.job_status import JobStatus

IN_PROGRESS_STATUSES = {JobStatus.QUEUED.value, JobStatus.TRANSCRIBING.value}


def save_job(session: Session, job: Job) -> Job:
    job.updated_at = datetime.utcnow()
    session.add(job)
    session.commit()
    session.refresh(job)
    return job


def can_upload_audio(job: Job) -> bool:
    return job.status not in IN_PROGRESS_STATUSES


def can_start_transcription(job: Job) -> tuple[bool, str | None]:
    if not job.input_path:
        return False, "No audio uploaded"

    if job.status in IN_PROGRESS_STATUSES:
        return False, "Transcription already in progress"

    if job.status == JobStatus.TRANSCRIBED.value:
        return False, "Transcript already generated for this upload"

    return True, None


def can_worker_transcribe(job: Job) -> bool:
    return job.status == JobStatus.QUEUED.value and bool(job.input_path)
