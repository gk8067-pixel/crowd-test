"""
Celery Worker Configuration
"""
from celery import Celery
from celery.schedules import crontab
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Celery
celery_app = Celery(
    "survey_system",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),
    include=["celery_tasks"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Taipei",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)

# Celery Beat Schedule (Periodic Tasks)
celery_app.conf.beat_schedule = {
    "cleanup-old-responses": {
        "task": "celery_tasks.cleanup_old_responses",
        "schedule": crontab(hour=2, minute=0),  # Run daily at 2 AM
    },
    "generate-daily-report": {
        "task": "celery_tasks.generate_daily_report",
        "schedule": crontab(hour=1, minute=0),  # Run daily at 1 AM
    },
    "update-survey-statistics": {
        "task": "celery_tasks.update_survey_statistics",
        "schedule": crontab(minute="*/15"),  # Run every 15 minutes
    },
}

if __name__ == "__main__":
    celery_app.start()