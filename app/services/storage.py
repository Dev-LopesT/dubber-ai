from pathlib import Path

BASE_STORAGE = Path("storage")


def ensure_job_dirs(job_id: str) -> Path:
    job_dir = BASE_STORAGE / "jobs" / job_id
    input_dir = job_dir / "input"
    output_dir = job_dir / "output"

    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    return job_dir