from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
from app.models import Job
from app.db import engine

router = APIRouter()


@router.post("/jobs")
def create_new_job():
    job = Job()

    with Session(engine) as session:
        session.add(job)
        session.commit()
        session.refresh(job)

    return job


@router.get("/jobs/{job_id}")
def get_job(job_id: str):
    with Session(engine) as session:
        statement = select(Job).where(Job.id == job_id)
        job = session.exec(statement).first()

        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        return job