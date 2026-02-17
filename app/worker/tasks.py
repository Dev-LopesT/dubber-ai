from sqlmodel import Session, select
from celery.exceptions import SoftTimeLimitExceeded

from app.worker.celery_app import celery_app
from app.db import engine
from app.models import Job
from app.services.jobs import save_job
from app.services.storage import get_job_output_dir
from app.services.transcription import transcribe_file
from app.job_status import JobStatus


@celery_app.task(acks_late=True, soft_time_limit=1200, time_limit=1500)
def transcribe_job_task(job_id: str):
    with Session(engine) as session:
        job = session.exec(select(Job).where(Job.id == job_id)).first()
        if not job:
            return

        if job.status != JobStatus.QUEUED.value or not job.input_path:
            return

        try:
            job.status = JobStatus.TRANSCRIBING.value
            save_job(session, job)

            transcript_text = transcribe_file(job.input_path)

            output_dir = get_job_output_dir(job_id)
            transcript_path = output_dir / "transcript.txt"
            transcript_path.write_text(transcript_text, encoding="utf-8")

            job.transcript_path = str(transcript_path)
            job.status = JobStatus.TRANSCRIBED.value
            job.error_message = None
            save_job(session, job)

        except SoftTimeLimitExceeded:
            job.status = JobStatus.ERROR.value
            job.error_message = "Transcription timed out"
            save_job(session, job)
        except Exception as e:
            job.status = JobStatus.ERROR.value
            job.error_message = str(e)
            save_job(session, job)
