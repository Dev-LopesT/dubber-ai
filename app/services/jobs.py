from datetime import datetime
from sqlmodel import Session
from app.models import Job


def save_job(session: Session, job: Job) -> Job:
    job.updated_at = datetime.utcnow()
    session.add(job)
    session.commit()
    session.refresh(job)
    return job