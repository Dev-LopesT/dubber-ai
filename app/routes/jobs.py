from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlmodel import Session, select
from pathlib import Path
import shutil

from app.job_status import JobStatus
from app.models import Job
from app.db import engine
from app.services.storage import ensure_job_dirs, get_job_input_dir
from app.services.jobs import save_job, can_upload_audio, can_start_transcription
from app.worker.tasks import transcribe_job_task

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

        if not can_upload_audio(job):
            raise HTTPException(
                status_code=409,
                detail="Cannot upload while transcription is in progress"
            )

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
        job.status = JobStatus.UPLOADED.value
        job.transcript_path = None
        job.error_message = None

        session.add(job)
        session.commit()
        session.refresh(job)

        return {
            "id": job.id,
            "status": job.status,
            "input_path": job.input_path,
            "filename_saved": standardized_filename,
        }

@router.post("/jobs/{job_id}/transcribe")
def start_transcription(job_id: str):
    with Session(engine) as session:
        job = session.exec(select(Job).where(Job.id == job_id)).first()

        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        can_start, reason = can_start_transcription(job)
        if not can_start:
            if reason == "No audio uploaded":
                raise HTTPException(status_code=400, detail=reason)
            raise HTTPException(status_code=409, detail=reason)

        job.status = JobStatus.QUEUED.value
        job.error_message = None
        save_job(session, job)

        transcribe_job_task.delay(job_id)

        return {"id": job.id, "status": job.status}

@router.get("/jobs/{job_id}/transcript")
def get_transcript(job_id: str):
    with Session(engine) as session:
        job = session.exec(select(Job).where(Job.id == job_id)).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        if job.status != JobStatus.TRANSCRIBED.value or not job.transcript_path:
            raise HTTPException(status_code=409, detail="Transcript not available yet")

        path = Path(job.transcript_path)
        if not path.exists():
            raise HTTPException(status_code=500, detail="Transcript file is missing")

        return FileResponse(path, media_type="text/plain", filename="transcript.txt")
