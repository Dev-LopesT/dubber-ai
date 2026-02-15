from pathlib import Path

BASE_STORAGE = Path("storage")


def get_job_dir(job_id: str) -> Path:
    return BASE_STORAGE / "jobs" / job_id


def get_job_input_dir(job_id: str) -> Path:
    return get_job_dir(job_id) / "input"


def get_job_output_dir(job_id: str) -> Path:
    return get_job_dir(job_id) / "output"


def ensure_job_dirs(job_id: str) -> Path:
    job_dir = get_job_dir(job_id)
    input_dir = get_job_input_dir(job_id)
    output_dir = get_job_output_dir(job_id)

    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    return job_dir
