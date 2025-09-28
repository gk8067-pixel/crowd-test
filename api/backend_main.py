# backend/app/main.py
from fastapi import FastAPI, Depends, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
import csv
from io import StringIO
from datetime import datetime, timedelta
import redis
import logging

from .database import get_db, engine
from .models import Video, Variant, Experiment, MetricsRaw, MetricsAgg
from .schemas import (
    VideoCreate, VideoResponse, VariantCreate, VariantResponse,
    ExperimentCreate, ExperimentResponse, ExperimentResults
)
from .utils import normalize_url
from .statistics import calculate_z_test
from .tasks import trigger_youtube_ingest

app = FastAPI(title="Crowd Test API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger(__name__)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    health_status = {
        "api": "ok",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Check database
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        health_status["database"] = "ok"
    except Exception as e:
        health_status["database"] = f"error: {str(e)}"
    
    # Check Redis
    try:
        r = redis.from_url("redis://localhost:6379")
        r.ping()
        health_status["redis"] = "ok"
    except Exception as e:
        health_status["redis"] = f"error: {str(e)}"
    
    return health_status

@app.post("/videos", response_model=VideoResponse)
def create_or_get_video(video_data: VideoCreate, db: Session = Depends(get_db)):
    """Create or return existing video"""
    # Check if video exists
    existing = db.query(Video).filter(
        Video.platform == video_data.platform,
        Video.external_id == video_data.external_id
    ).first()
    
    if existing:
        return existing
    
    # Create new video
    video = Video(
        platform=video_data.platform,
        external_id=video_data.external_id,
        title=video_data.title or f"Video {video_data.external_id}",
        channel_id=getattr(video_data, 'channel_id', None)
    )
    db.add(video)
    db.commit()
    db.refresh(video)
    return video

@app.post("/videos/{video_id}/variants", response_model=VariantResponse)
def create_variant(video_id: str, variant_data: VariantCreate, db: Session = Depends(get_db)):
    """Create a variant for a video"""
    # Verify video exists
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Normalize thumbnail URL
    thumbnail_url = None
    if variant_data.thumbnail_url:
        thumbnail_url = normalize_url(variant_data.thumbnail_url)
    
    # Generate variant key if not provided
    variant_count = db.query(Variant).filter(Variant.video_id == video_id).count()
    variant_key = getattr(variant_data, 'variant_key', chr(65 + variant_count))  # A, B, C...
    
    variant = Variant(
        video_id=video_id,
        variant_key=variant_key,
        title=variant_data.title,
        description=variant_data.description,
        thumbnail_url=thumbnail_url
    )
    db.add(variant)
    db.commit()
    db.refresh(variant)
    return variant

@app.post("/experiments", response_model=ExperimentResponse)
def create_experiment(experiment_data: ExperimentCreate, db: Session = Depends(get_db)):
    """Create a new experiment"""
    # Verify video exists and has variants
    video = db.query(Video).filter(Video.id == experiment_data.video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    variant_count = db.query(Variant).filter(Variant.video_id == experiment_data.video_id).count()
    if variant_count < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 variants to run experiment")
    
    experiment = Experiment(
        name=experiment_data.name,
        video_id=experiment_data.video_id,
        primary_metric=experiment_data.primary_metric,
        secondary_metrics=experiment_data.secondary_metrics or [],
        start_at=datetime.utcnow(),
        stop_rules=experiment_data.stop_rules or {},
        status="running"
    )
    db.add(experiment)
    db.commit()
    db.refresh(experiment)
    return experiment

@app.get("/experiments/{experiment_id}", response_model=ExperimentResponse)
def get_experiment(experiment_id: str, db: Session = Depends(get_db)):
    """Get experiment details"""
    experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return experiment

@app.get("/experiments/{experiment_id}/results", response_model=ExperimentResults)
def get_experiment_results(experiment_id: str, db: Session = Depends(get_db)):
    """Get experiment results with statistical analysis"""
    experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    # Get variants
    variants = db.query(Variant).filter(Variant.video_id == experiment.video_id).all()
    
    # Get latest aggregated metrics for each variant
    results = []
    for variant in variants:
        latest_metrics = db.query(MetricsAgg).filter(
            MetricsAgg.variant_id == variant.id
        ).order_by(MetricsAgg.date.desc()).first()
        
        if latest_metrics:
            # Calculate CTR if we have impressions
            ctr = 0
            if latest_metrics.impressions > 0:
                ctr = latest_metrics.clicks / latest_metrics.impressions
            
            # Calculate like rate
            like_rate = 0
            if latest_metrics.views > 0:
                like_rate = latest_metrics.likes / latest_metrics.views
            
            results.append({
                "variant_id": str(variant.id),
                "variant_key": variant.variant_key,
                "views": latest_metrics.views,
                "likes": latest_metrics.likes,
                "comments": latest_metrics.comments,
                "shares": latest_metrics.shares,
                "impressions": latest_metrics.impressions,
                "clicks": latest_metrics.clicks,
                "ctr": ctr,
                "like_rate": like_rate
            })
    
    # Perform statistical test if we have at least 2 variants with data
    statistical_results = None
    winner = None
    
    if len(results) >= 2:
        # Use primary metric for comparison
        if experiment.primary_metric == "ctr":
            # Compare CTR between first two variants
            variant_a = results[0]
            variant_b = results[1]
            
            if variant_a["impressions"] > 0 and variant_b["impressions"] > 0:
                z_stat, p_value, ci_a, ci_b = calculate_z_test(
                    variant_a["clicks"], variant_a["impressions"],
                    variant_b["clicks"], variant_b["impressions"]
                )
                
                statistical_results = {
                    "z_statistic": z_stat,
                    "p_value": p_value,
                    "variant_a_ci": ci_a,
                    "variant_b_ci": ci_b,
                    "significant": p_value < 0.05
                }
                
                # Determine winner
                if statistical_results["significant"]:
                    winner = variant_a["variant_key"] if variant_a["ctr"] > variant_b["ctr"] else variant_b["variant_key"]
    
    return ExperimentResults(
        experiment_id=str(experiment.id),
        status=experiment.status,
        variants=results,
        statistical_results=statistical_results,
        winner=winner
    )

@app.get("/experiments/{experiment_id}/export.csv")
def export_experiment_csv(experiment_id: str, db: Session = Depends(get_db)):
    """Export experiment data as CSV"""
    experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    # Get all metrics data
    from sqlalchemy import join
    
    query = db.query(
        MetricsAgg,
        Variant.variant_key
    ).join(Variant, MetricsAgg.variant_id == Variant.id).filter(
        Variant.video_id == experiment.video_id
    ).order_by(MetricsAgg.date, Variant.variant_key)
    
    results = query.all()
    
    # Create CSV
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'date', 'variant_key', 'views', 'likes', 'comments', 
        'shares', 'impressions', 'clicks', 'watch_time_sec'
    ])
    
    # Write data
    for metrics, variant_key in results:
        writer.writerow([
            metrics.date.strftime('%Y-%m-%d'),
            variant_key,
            metrics.views,
            metrics.likes,
            metrics.comments,
            metrics.shares,
            metrics.impressions,
            metrics.clicks,
            metrics.watch_time_sec
        ])
    
    output.seek(0)
    
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=experiment_{experiment_id}.csv"}
    )

@app.post("/ingest/youtube")
def trigger_youtube_ingest_endpoint():
    """Trigger YouTube data ingestion (internal use)"""
    trigger_youtube_ingest.delay()
    return {"message": "YouTube ingestion triggered"}

@app.post("/tools/normalize-url")
def normalize_url_endpoint(url: str):
    """Test URL normalization"""
    normalized = normalize_url(url)
    return {
        "original": url,
        "normalized": normalized
    }