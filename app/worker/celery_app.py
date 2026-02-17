from celery import Celery

celery_app = Celery(
    "dubber_ai",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
)

# Register local tasks module on worker startup.
import app.worker.tasks  # noqa: F401,E402
