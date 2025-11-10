"""
FastAPI entry point for Geo-Resilience Initiative
Main API server for geospatial analysis endpoints
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
import uvicorn

from core.config import settings
from modules.ndvi_module import analyze_ndvi_deforestation
from modules.sar_module import analyze_flood_sar
from modules.afforestation_module import analyze_afforestation_suitability
from database.db_config import init_db

# Initialize FastAPI app
app = FastAPI(
    title="Geo-Resilience Initiative API",
    description="Geospatial intelligence platform for wildfire, flood, and afforestation analysis",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database connection on application startup"""
    init_db()

# Pydantic models for request/response
class BBoxRequest(BaseModel):
    """Bounding box request model"""
    bbox: List[float] = Field(
        ..., 
        description="Bounding box as [min_lon, min_lat, max_lon, max_lat]",
        min_items=4,
        max_items=4
    )
    start_date: str = Field(
        ..., 
        description="Start date in YYYY-MM-DD format"
    )
    end_date: str = Field(
        ..., 
        description="End date in YYYY-MM-DD format"
    )

class AnalysisResponse(BaseModel):
    """Standard analysis response model"""
    status: str
    type: str
    area_km2: float
    geojson: dict
    metadata: Optional[dict] = None

@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "Geo-Resilience Initiative API",
        "version": "1.0.0",
        "endpoints": {
            "ndvi": "/analyze/ndvi",
            "flood": "/analyze/flood",
            "afforestation": "/analyze/afforestation"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "geo-resilience-api"}

@app.post("/analyze/ndvi", response_model=AnalysisResponse)
async def analyze_ndvi(request: BBoxRequest):
    """
    NDVI and deforestation analysis endpoint
    
    Analyzes NDVI changes using Sentinel-2 data to detect deforestation
    within the specified bounding box and date range.
    """
    try:
        # Validate date format
        start_date = datetime.strptime(request.start_date, "%Y-%m-%d")
        end_date = datetime.strptime(request.end_date, "%Y-%m-%d")
        
        if len(request.bbox) != 4:
            raise HTTPException(status_code=400, detail="Bounding box must contain exactly 4 values [min_lon, min_lat, max_lon, max_lat]")
        
        # Run NDVI analysis
        result = analyze_ndvi_deforestation(
            bbox=request.bbox,
            start_date=request.start_date,
            end_date=request.end_date
        )
        
        return AnalysisResponse(
            status="success",
            type="ndvi",
            area_km2=result["area_km2"],
            geojson=result["geojson"],
            metadata=result.get("metadata")
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/analyze/flood", response_model=AnalysisResponse)
async def analyze_flood(request: BBoxRequest):
    """
    Flood detection analysis endpoint using Sentinel-1 SAR data
    
    Uses SAR (Synthetic Aperture Radar) to detect flooded areas
    which are visible even through cloud cover.
    """
    try:
        # Validate date format
        start_date = datetime.strptime(request.start_date, "%Y-%m-%d")
        end_date = datetime.strptime(request.end_date, "%Y-%m-%d")
        
        if len(request.bbox) != 4:
            raise HTTPException(status_code=400, detail="Bounding box must contain exactly 4 values [min_lon, min_lat, max_lon, max_lat]")
        
        # Run SAR flood analysis
        result = analyze_flood_sar(
            bbox=request.bbox,
            start_date=request.start_date,
            end_date=request.end_date
        )
        
        return AnalysisResponse(
            status="success",
            type="flood",
            area_km2=result["area_km2"],
            geojson=result["geojson"],
            metadata=result.get("metadata")
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/analyze/afforestation", response_model=AnalysisResponse)
async def analyze_afforestation(request: BBoxRequest):
    """
    Afforestation suitability analysis endpoint
    
    Identifies suitable zones for afforestation using DEM (Digital Elevation Model)
    and OpenStreetMap data for land use constraints.
    """
    try:
        # Validate date format
        start_date = datetime.strptime(request.start_date, "%Y-%m-%d")
        end_date = datetime.strptime(request.end_date, "%Y-%m-%d")
        
        if len(request.bbox) != 4:
            raise HTTPException(status_code=400, detail="Bounding box must contain exactly 4 values [min_lon, min_lat, max_lon, max_lat]")
        
        # Run afforestation analysis
        result = analyze_afforestation_suitability(
            bbox=request.bbox,
            start_date=request.start_date,
            end_date=request.end_date
        )
        
        return AnalysisResponse(
            status="success",
            type="afforestation",
            area_km2=result["area_km2"],
            geojson=result["geojson"],
            metadata=result.get("metadata")
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )

