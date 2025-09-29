"""
Celery Tasks
"""
from celery_worker import celery_app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from backend_models import Response, Survey
from backend_statistics import calculate_survey_statistics
import logging

load_dotenv()

logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/survey_db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@celery_app.task(name="celery_tasks.cleanup_old_responses")
def cleanup_old_responses(days: int = 90):
    """
    Clean up responses older than specified days
    """
    try:
        db = SessionLocal()
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        deleted_count = db.query(Response).filter(
            Response.submitted_at < cutoff_date
        ).delete()
        
        db.commit()
        logger.info(f"Cleaned up {deleted_count} old responses")
        return {"status": "success", "deleted": deleted_count}
    except Exception as e:
        logger.error(f"Error in cleanup_old_responses: {str(e)}")
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


@celery_app.task(name="celery_tasks.generate_daily_report")
def generate_daily_report():
    """
    Generate daily statistics report for all active surveys
    """
    try:
        db = SessionLocal()
        active_surveys = db.query(Survey).filter(Survey.is_active == True).all()
        
        reports = []
        for survey in active_surveys:
            stats = calculate_survey_statistics(db, survey.id)
            reports.append({
                "survey_id": survey.id,
                "survey_title": survey.title,
                "statistics": stats
            })
        
        logger.info(f"Generated daily report for {len(reports)} surveys")
        return {"status": "success", "reports": reports}
    except Exception as e:
        logger.error(f"Error in generate_daily_report: {str(e)}")
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


@celery_app.task(name="celery_tasks.update_survey_statistics")
def update_survey_statistics():
    """
    Update statistics for all active surveys
    """
    try:
        db = SessionLocal()
        active_surveys = db.query(Survey).filter(Survey.is_active == True).all()
        
        updated_count = 0
        for survey in active_surveys:
            # Calculate and cache statistics
            stats = calculate_survey_statistics(db, survey.id)
            if stats:
                updated_count += 1
        
        logger.info(f"Updated statistics for {updated_count} surveys")
        return {"status": "success", "updated": updated_count}
    except Exception as e:
        logger.error(f"Error in update_survey_statistics: {str(e)}")
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


@celery_app.task(name="celery_tasks.send_survey_notification")
def send_survey_notification(survey_id: int, user_ids: list):
    """
    Send notification to users about a new survey
    """
    try:
        # Placeholder for email/notification logic
        logger.info(f"Sending notifications for survey {survey_id} to {len(user_ids)} users")
        return {"status": "success", "notified": len(user_ids)}
    except Exception as e:
        logger.error(f"Error in send_survey_notification: {str(e)}")
        return {"status": "error", "message": str(e)}


@celery_app.task(name="celery_tasks.export_survey_data")
def export_survey_data(survey_id: int, format: str = "csv"):
    """
    Export survey data to specified format
    """
    try:
        db = SessionLocal()
        # Placeholder for export logic
        logger.info(f"Exporting survey {survey_id} data to {format}")
        return {"status": "success", "format": format}
    except Exception as e:
        logger.error(f"Error in export_survey_data: {str(e)}")
        return {"status": "error", "message": str(e)}
    finally:
        db.close()