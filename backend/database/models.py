"""
SQLAlchemy ORM models for Geo-Resilience Initiative
Database models for storing analysis results
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Text
from sqlalchemy.dialects.postgresql import JSONB
from geoalchemy2 import Geometry
from datetime import datetime
from database.db_config import Base

class AnalysisResult(Base):
    """
    Model for storing analysis results in PostgreSQL/PostGIS
    """
    __tablename__ = "analysis_results"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Analysis metadata
    analysis_type = Column(String, nullable=False, index=True)  # 'ndvi', 'flood', 'afforestation'
    start_date = Column(String, nullable=False)
    end_date = Column(String, nullable=False)
    
    # Bounding box (stored as JSON)
    bbox = Column(JSON, nullable=False)
    
    # Spatial data (PostGIS geometry)
    geometry = Column(Geometry('MULTIPOLYGON', srid=4326), nullable=True)
    
    # Results
    area_km2 = Column(Float, nullable=False)
    
    # GeoJSON stored as JSONB for efficient querying
    geojson = Column(JSONB, nullable=True)
    
    # Additional metadata
    metadata = Column(JSONB, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<AnalysisResult(id={self.id}, type={self.analysis_type}, area={self.area_km2} km²)>"

