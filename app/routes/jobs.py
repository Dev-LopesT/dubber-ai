from fastapi import APIRouter, HTTPException, UploadFile, File
from sqlmodel import Session, select
from pathlib import Path
import shutil

from app.models import Job
from app.db import engine
from app.services.storage import ensure_job_dirs, get_job_input_dir

router = APIRouter()

ALLOWED_EXTENSIONS = {".mp3", ".m4a", ".wav", ".flac", ".aac", ".ogg"}


@router.post("/jobs")
def create_job():
    with Session(engine) as session:
        job = Job()
        session.add(job)
        session.commit()
        session.refresh(job)

        ensure_job_dirs(job.id)

        return {
            "id": job.id,
            "status": job.status,
            "input_path": job.input_path,
        }


@router.get("/jobs/{job_id}")
def get_job(job_id: str):
    with Session(engine) as session:
        job = session.exec(select(Job).where(Job.id == job_id)).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        return {
            "id": job.id,
            "status": job.status,
            "input_path": job.input_path,
        }


@router.post("/jobs/{job_id}/upload")
def upload_audio(job_id: str, file: UploadFile = File(...)):
    with Session(engine) as session:
        job = session.exec(select(Job).where(Job.id == job_id)).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        if not file.filename:
            raise HTTPException(status_code=400, detail="Missing filename")

        # Use file extension from the uploaded filename.
        extension = Path(file.filename).suffix.lower()

        if extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=415,
                detail=f"Unsupported file type: {extension}"
            )

        # Ensure storage directories exist.
        ensure_job_dirs(job_id)
        input_dir = get_job_input_dir(job_id)

        # Store uploaded audio with a standardized filename.
        standardized_filename = f"input{extension}"
        dest_path = input_dir / standardized_filename

        # Persist upload to disk.
        with dest_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Update job metadata after successful upload.
        job.input_path = str(dest_path)
        job.status = "uploaded"

        session.add(job)
        session.commit()
        session.refresh(job)

        return {
            "id": job.id,
            "status": job.status,
            "input_path": job.input_path,
            "filename_saved": standardized_filename,
        }
