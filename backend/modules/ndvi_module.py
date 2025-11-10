"""
NDVI Module for deforestation detection
Analyzes NDVI changes from Sentinel-2 data to identify deforestation areas
"""

import numpy as np
import geopandas as gpd
from shapely.geometry import Polygon, MultiPolygon
from typing import List, Dict
import os
from datetime import datetime

from core.config import settings
from core.utils import (
    bbox_to_polygon,
    calculate_area_km2,
    polygons_to_geojson,
    calculate_ndvi,
    calculate_ndvi_change,
    validate_bbox
)

# Try to import real satellite data fetcher
try:
    from modules.satellite_fetcher import fetch_sentinel2_real, REAL_DATA_AVAILABLE
except ImportError:
    REAL_DATA_AVAILABLE = False
    fetch_sentinel2_real = None

def fetch_sentinel2_data(bbox: List[float], date: str) -> Dict[str, np.ndarray]:
    """
    Fetch Sentinel-2 data for given bounding box and date
    
    Tries to fetch real data from Planetary Computer first, falls back to mock data if unavailable.
    
    Args:
        bbox: Bounding box [min_lon, min_lat, max_lon, max_lat]
        date: Date string in YYYY-MM-DD format
    
    Returns:
        Dictionary with 'red' and 'nir' bands as numpy arrays
    """
    # Try to fetch real data first - PRIORITIZE REAL DATA
    if REAL_DATA_AVAILABLE and fetch_sentinel2_real:
        real_data = fetch_sentinel2_real(bbox, date)
        if real_data is not None:
            print(f"✅ Using REAL Sentinel-2 data for {date}")
            return real_data
        else:
            # Try a few more times with nearby dates if available
            from datetime import datetime, timedelta
            try:
                date_obj = datetime.strptime(date, "%Y-%m-%d")
                for days_offset in [1, -1, 2, -2, 3, -3]:  # Try ±1, ±2, ±3 days
                    alt_date = (date_obj + timedelta(days=days_offset)).strftime("%Y-%m-%d")
                    real_data = fetch_sentinel2_real(bbox, alt_date)
                    if real_data is not None:
                        print(f"✅ Using REAL Sentinel-2 data from nearby date: {alt_date} (requested: {date})")
                        return real_data
            except Exception:
                pass
            print(f"⚠️ No real data found near {date}, using mock data")
    
    # Fallback to mock data
    bbox_poly = bbox_to_polygon(bbox)
    min_lon, min_lat, max_lon, max_lat = bbox
    
    # Generate a simple grid for demonstration
    np.random.seed(hash(date) % 2**32)  # Deterministic based on date
    
    # Create synthetic bands (simulating vegetation patterns)
    size = 100  # Grid size
    red = np.random.uniform(0.1, 0.3, (size, size))
    nir = np.random.uniform(0.2, 0.5, (size, size))
    
    # Add some spatial structure (vegetation patches)
    x = np.linspace(min_lon, max_lon, size)
    y = np.linspace(min_lat, max_lat, size)
    xx, yy = np.meshgrid(x, y)
    
    # Simulate higher vegetation in some areas
    vegetation_mask = np.sin(xx * 10) * np.cos(yy * 10) > 0
    nir[vegetation_mask] += 0.2
    red[vegetation_mask] -= 0.05
    
    return {
        "red": red,
        "nir": nir,
        "transform": None,
        "crs": "EPSG:4326"
    }

def analyze_ndvi_deforestation(
    bbox: List[float],
    start_date: str,
    end_date: str
) -> Dict:
    """
    Analyze NDVI changes to detect deforestation
    
    Compares NDVI between start_date and end_date to identify areas
    where vegetation has significantly decreased (potential deforestation).
    
    Args:
        bbox: Bounding box [min_lon, min_lat, max_lon, max_lat]
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    
    Returns:
        Dictionary with:
            - area_km2: Total area of detected deforestation
            - geojson: GeoJSON FeatureCollection of deforestation polygons
            - metadata: Additional analysis metadata
    """
    # Validate inputs
    validate_bbox(bbox)
    
    print(f"Analyzing NDVI for bbox {bbox} from {start_date} to {end_date}")
    
    # Fetch Sentinel-2 data for both time periods
    data_before = fetch_sentinel2_data(bbox, start_date)
    data_after = fetch_sentinel2_data(bbox, end_date)
    
    # Calculate NDVI for both periods
    ndvi_before = calculate_ndvi(data_before["red"], data_before["nir"])
    ndvi_after = calculate_ndvi(data_after["red"], data_after["nir"])
    
    # Calculate NDVI change
    ndvi_change = calculate_ndvi_change(ndvi_before, ndvi_after)
    
    # Threshold for deforestation detection
    # Negative change threshold (e.g., -0.2 means 20% drop in NDVI)
    deforestation_threshold = -0.15
    
    # Identify deforestation areas (significant negative NDVI change)
    deforestation_mask = ndvi_change < deforestation_threshold
    
    # Convert mask to polygons
    deforestation_areas = mask_to_polygons(
        deforestation_mask,
        bbox,
        min_area_pixels=10  # Minimum area filter to remove noise
    )
    
    # Calculate total area
    total_area = 0.0
    for geom in deforestation_areas:
        total_area += calculate_area_km2(geom)
    
    # Create GeoJSON
    geojson = polygons_to_geojson(
        deforestation_areas,
        properties=[
            {
                "area_km2": round(calculate_area_km2(geom), 4),
                "ndvi_change": round(float(np.mean(ndvi_change[deforestation_mask])), 3),
                "detection_method": "ndvi_threshold"
            }
            for geom in deforestation_areas
        ]
    )
    
    # Calculate statistics
    mean_ndvi_before = float(np.nanmean(ndvi_before))
    mean_ndvi_after = float(np.nanmean(ndvi_after))
    mean_change = float(np.nanmean(ndvi_change))
    
    metadata = {
        "analysis_date": datetime.now().isoformat(),
        "start_date": start_date,
        "end_date": end_date,
        "bbox": bbox,
        "mean_ndvi_before": round(mean_ndvi_before, 3),
        "mean_ndvi_after": round(mean_ndvi_after, 3),
        "mean_ndvi_change": round(mean_change, 3),
        "deforestation_threshold": deforestation_threshold,
        "num_deforestation_patches": len(deforestation_areas)
    }
    
    print(f"Detected {len(deforestation_areas)} deforestation areas totaling {total_area:.2f} km²")
    
    return {
        "area_km2": round(total_area, 4),
        "geojson": geojson,
        "metadata": metadata
    }

def mask_to_polygons(
    mask: np.ndarray,
    bbox: List[float],
    min_area_pixels: int = 10
) -> List[Polygon]:
    """
    Convert binary mask to Shapely polygons
    
    Args:
        mask: Binary numpy array (True/False or 1/0)
        bbox: Original bounding box [min_lon, min_lat, max_lon, max_lat]
        min_area_pixels: Minimum number of pixels to keep a polygon
    
    Returns:
        List of Shapely Polygon objects
    """
    from shapely.geometry import shape
    
    try:
        from rasterio import features
        from rasterio.transform import from_bounds
    except ImportError:
        # Fallback if rasterio.features not available
        return []
    
    # Get bounding box coordinates
    min_lon, min_lat, max_lon, max_lat = bbox
    
    # Calculate resolution for area filtering
    height, width = mask.shape
    x_res = (max_lon - min_lon) / width
    y_res = (max_lat - min_lat) / height
    
    # Create transform for the mask using rasterio's from_bounds
    transform = from_bounds(min_lon, min_lat, max_lon, max_lat, width, height)
    
    # Polygonize the mask
    shapes = features.shapes(mask.astype(np.uint8), transform=transform)
    
    polygons = []
    for geom, value in shapes:
        if value == 1:  # Only keep True/1 values
            poly = shape(geom)
            if poly.is_valid and poly.area > 0:
                # Filter by minimum area (in pixel space approximation)
                # Convert degrees to approximate meters (1 degree ≈ 111,320 meters)
                min_area_deg2 = min_area_pixels * (x_res * 111.32) * (y_res * 111.32) / (111.32 * 111.32)
                if poly.area > min_area_deg2:
                    polygons.append(poly)
    
    return polygons

