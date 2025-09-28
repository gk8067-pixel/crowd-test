# backend/app/models.py
from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, ForeignKey, Date, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class Video(Base):
    __tablename__ = "videos"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform = Column(Text, nullable=False)
    external_id = Column(Text, nullable=False, unique=True)
    title = Column(Text, nullable=False)
    channel_id = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    variants = relationship("Variant", back_populates="video")
    experiments = relationship("Experiment", back_populates="video")

class Variant(Base):
    __tablename__ = "variants"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id"), nullable=False)
    variant_key = Column(Text, nullable=False)
    title = Column(Text)
    description = Column(Text)
    thumbnail_url = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    video = relationship("Video", back_populates="variants")
    metrics_raw = relationship("MetricsRaw", back_populates="variant")
    metrics_agg = relationship("MetricsAgg", back_populates="variant")

class Experiment(Base):
    __tablename__ = "experiments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id"), nullable=False)
    primary_metric = Column(Text, nullable=False)
    secondary_metrics = Column(JSON)
    start_at = Column(DateTime(timezone=True), nullable=False)
    end_at = Column(DateTime(timezone=True))
    stop_rules = Column(JSON)
    status = Column(Text, nullable=False, default="running")
    
    video = relationship("Video", back_populates="experiments")

class MetricsRaw(Base):
    __tablename__ = "metrics_raw"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id"), nullable=False)
    variant_id = Column(UUID(as_uuid=True), ForeignKey("variants.id"), nullable=False)
    ts = Column(DateTime(timezone=True), nullable=False)
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    watch_time_sec = Column(Integer, default=0)
    source = Column(Text, default="youtube")
    
    video = relationship("Video")
    variant = relationship("Variant", back_populates="metrics_raw")

class MetricsAgg(Base):
    __tablename__ = "metrics_agg"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id"), nullable=False)
    variant_id = Column(UUID(as_uuid=True), ForeignKey("variants.id"), nullable=False)
    date = Column(Date, nullable=False)
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    watch_time_sec = Column(Integer, default=0)
    
    video = relationship("Video")
    variant = relationship("Variant", back_populates="metrics_agg")
    
    __table_args__ = (
        {"schema": None},
    )

# Create unique constraint for metrics_agg
from sqlalchemy import UniqueConstraint
MetricsAgg.__table_args__ = (
    UniqueConstraint('video_id', 'variant_id', 'date', name='_video_variant_date_uc'),
)