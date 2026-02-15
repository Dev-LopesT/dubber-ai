from pathlib import Path

BASE_STORAGE = Path("storage")


def get_job_dir(job_id: str) -> Path:
    return BASE_STORAGE / "jobs" / job_id


def get_job_input_dir(job_id: str) -> Path:
    path = get_job_dir(job_id) / "input"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_job_output_dir(job_id: str) -> Path:
    path = get_job_dir(job_id) / "output"
    path.mkdir(parents=True, exist_ok=True)
    return path


def ensure_job_dirs(job_id: str) -> Path:
    job_dir = get_job_dir(job_id)
    get_job_input_dir(job_id)
    get_job_output_dir(job_id)
    return job_dir
