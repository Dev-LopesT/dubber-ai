from sqlmodel import Session, select

from app.db import engine
from app.models import Job
from app.services.jobs import save_job
from app.services.storage import get_job_output_dir
from app.services.transcription import transcribe_file


def run_transcription(job_id: str) -> None:
    with Session(engine) as session:
        job = session.exec(select(Job).where(Job.id == job_id)).first()
        if not job:
            return

        if not job.input_path:
            job.status = "error"
            job.error_message = "No audio uploaded for this job"
            save_job(session, job)
            return

        try:
            job.status = "transcribing"
            job.error_message = None
            save_job(session, job)

            transcript_text = transcribe_file(job.input_path)

            output_dir = get_job_output_dir(job_id)
            transcript_path = output_dir / "transcript.txt"
            transcript_path.write_text(transcript_text, encoding="utf-8")

            job.transcript_path = str(transcript_path)
            job.status = "transcribed"
            save_job(session, job)

        except Exception as e:
            job.status = "error"
            job.error_message = str(e)
            save_job(session, job)