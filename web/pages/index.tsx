# backend/app/tasks.py
from celery import Celery
from celery.schedules import crontab
import os
import logging
import random
from datetime import datetime, date, timedelta
import requests
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import insert

from .database import engine
from .models import Video, Variant, Experiment, MetricsRaw, MetricsAgg

# Configure Celery
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
celery_app = Celery('crowdtest', broker=REDIS_URL, backend=REDIS_URL)

# Configure Celery beat schedule
celery_app.conf.beat_schedule = {
    'ingest-youtube-data': {
        'task': 'app.tasks.ingest_youtube_data',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
}

celery_app.conf.timezone = 'UTC'

logger = logging.getLogger(__name__)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=60, retry_kwargs={'max_retries': 3})
def ingest_youtube_data(self):
    """
    Ingest YouTube data for all running experiments
    """
    logger.info("Starting YouTube data ingestion")
    
    db = SessionLocal()
    try:
        # Get all running experiments
        running_experiments = db.query(Experiment).filter(
            Experiment.status == "running"
        ).all()
        
        logger.info(f"Found {len(running_experiments)} running experiments")
        
        for experiment in running_experiments:
            try:
                # Get variants for this experiment
                variants = db.query(Variant).filter(
                    Variant.video_id == experiment.video_id
                ).all()
                
                for variant in variants:
                    # Fetch metrics for this variant
                    metrics_data = fetch_youtube_metrics(
                        experiment.video.external_id, 
                        variant.variant_key
                    )
                    
                    if metrics_data:
                        # Store raw metrics
                        raw_metric = MetricsRaw(
                            video_id=experiment.video_id,
                            variant_id=variant.id,
                            ts=datetime.utcnow(),
                            views=metrics_data.get('views', 0),
                            likes=metrics_data.get('likes', 0),
                            comments=metrics_data.get('comments', 0),
                            shares=metrics_data.get('shares', 0),
                            impressions=metrics_data.get('impressions', 0),
                            clicks=metrics_data.get('clicks', 0),
                            watch_time_sec=metrics_data.get('watch_time_sec', 0),
                            source='youtube'
                        )
                        db.add(raw_metric)
                        
                        # Aggregate to daily metrics (UPSERT)
                        today = date.today()
                        stmt = insert(MetricsAgg).values(
                            video_id=experiment.video_id,
                            variant_id=variant.id,
                            date=today,
                            views=metrics_data.get('views', 0),
                            likes=metrics_data.get('likes', 0),
                            comments=metrics_data.get('comments', 0),
                            shares=metrics_data.get('shares', 0),
                            impressions=metrics_data.get('impressions', 0),
                            clicks=metrics_data.get('clicks', 0),
                            watch_time_sec=metrics_data.get('watch_time_sec', 0)
                        )
                        
                        # On conflict, update the values
                        stmt = stmt.on_conflict_do_update(
                            index_elements=['video_id', 'variant_id', 'date'],
                            set_=dict(
                                views=stmt.excluded.views,
                                likes=stmt.excluded.likes,
                                comments=stmt.excluded.comments,
                                shares=stmt.excluded.shares,
                                impressions=stmt.excluded.impressions
