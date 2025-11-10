"""
Shared utility functions for geospatial processing
Raster operations, GeoJSON conversion, coordinate transformations
"""

import numpy as np
import geopandas as gpd
from shapely.geometry import box, Polygon, MultiPolygon
from shapely.ops import unary_union
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.crs import CRS
import json
from typing import List, Dict, Tuple, Optional

def bbox_to_polygon(bbox: List[float]) -> Polygon:
    """
    Convert bounding box [min_lon, min_lat, max_lon, max_lat] to Shapely Polygon
    
    Args:
        bbox: List of 4 floats representing [min_lon, min_lat, max_lon, max_lat]
    
    Returns:
        Shapely Polygon object
    """
    if len(bbox) != 4:
        raise ValueError("Bounding box must contain exactly 4 values")
    
    min_lon, min_lat, max_lon, max_lat = bbox
    return box(min_lon, min_lat, max_lon, max_lat)

def calculate_area_km2(geometry: Polygon | MultiPolygon) -> float:
    """
    Calculate area of geometry in square kilometers
    
    Args:
        geometry: Shapely Polygon or MultiPolygon
    
    Returns:
        Area in square kilometers
    """
    # Create GeoDataFrame with geometry in Web Mercator (EPSG:3857) for accurate area calculation
    gdf = gpd.GeoDataFrame([1], geometry=[geometry], crs="EPSG:4326")
    gdf = gdf.to_crs("EPSG:3857")  # Web Mercator projection
    
    # Calculate area in square meters, convert to km²
    area_m2 = gdf.geometry.area.iloc[0]
    area_km2 = area_m2 / 1_000_000
    
    return area_km2

def polygons_to_geojson(geometries: List[Polygon | MultiPolygon], properties: Optional[List[Dict]] = None) -> dict:
    """
    Convert list of Shapely polygons to GeoJSON FeatureCollection
    
    Args:
        geometries: List of Shapely Polygon or MultiPolygon objects
        properties: Optional list of property dictionaries for each geometry
    
    Returns:
        GeoJSON FeatureCollection dictionary
    """
    features = []
    
    for idx, geom in enumerate(geometries):
        # Convert geometry to GeoJSON format
        geojson_geom = gpd.GeoSeries([geom], crs="EPSG:4326").__geo_interface__["features"][0]["geometry"]
        
        # Get properties for this feature
        props = properties[idx] if properties and idx < len(properties) else {}
        
        features.append({
            "type": "Feature",
            "geometry": geojson_geom,
            "properties": props
        })
    
    return {
        "type": "FeatureCollection",
        "features": features
    }

def raster_to_geojson(
    raster_path: str,
    threshold: float = 0.5,
    crs: str = "EPSG:4326"
) -> dict:
    """
    Convert raster to GeoJSON by thresholding and polygonizing
    
    Args:
        raster_path: Path to raster file
        threshold: Threshold value for binary classification
        crs: Target CRS for output (default: EPSG:4326)
    
    Returns:
        GeoJSON FeatureCollection
    """
    import rasterio.features
    
    with rasterio.open(raster_path) as src:
        # Read raster data
        data = src.read(1)
        
        # Apply threshold (values >= threshold become True)
        binary = data >= threshold
        
        # Polygonize
        shapes = rasterio.features.shapes(binary.astype(np.uint8), transform=src.transform)
        
        # Filter to only include True values (above threshold)
        geometries = []
        for geom, value in shapes:
            if value == 1:  # True in binary mask
                poly = Polygon(geom["coordinates"][0])
                if poly.is_valid:
                    geometries.append(poly)
        
        # Merge nearby polygons
        if geometries:
            merged = unary_union(geometries)
            if isinstance(merged, Polygon):
                geometries = [merged]
            elif isinstance(merged, MultiPolygon):
                geometries = list(merged.geoms)
        
        # Convert to GeoDataFrame and reproject
        if geometries:
            gdf = gpd.GeoDataFrame(geometry=geometries, crs=src.crs)
            gdf = gdf.to_crs(crs)
            
            # Convert to GeoJSON
            return polygons_to_geojson(gdf.geometry.tolist())
    
    return {
        "type": "FeatureCollection",
        "features": []
    }

def clip_raster_to_bbox(
    raster_path: str,
    bbox: List[float],
    output_path: Optional[str] = None
) -> np.ndarray:
    """
    Clip raster to bounding box
    
    Args:
        raster_path: Path to input raster
        bbox: Bounding box [min_lon, min_lat, max_lon, max_lat]
        output_path: Optional path to save clipped raster
    
    Returns:
        Numpy array of clipped raster data
    """
    from rasterio import mask as rio_mask
    
    bbox_poly = bbox_to_polygon(bbox)
    
    with rasterio.open(raster_path) as src:
        # Create mask from bounding box
        gdf = gpd.GeoDataFrame([1], geometry=[bbox_poly], crs="EPSG:4326")
        
        # Reproject bbox to raster CRS if needed
        if src.crs != CRS.from_epsg(4326):
            gdf = gdf.to_crs(src.crs)
        
        # Clip raster
        out_image, out_transform = rio_mask.mask(src, gdf.geometry, crop=True)
        
        # Save if output path provided
        if output_path:
            out_meta = src.meta.copy()
            out_meta.update({
                "driver": "GTiff",
                "height": out_image.shape[1],
                "width": out_image.shape[2],
                "transform": out_transform
            })
            
            with rasterio.open(output_path, "w", **out_meta) as dest:
                dest.write(out_image)
        
        return out_image[0]  # Return first band

def calculate_ndvi(red_band: np.ndarray, nir_band: np.ndarray) -> np.ndarray:
    """
    Calculate NDVI (Normalized Difference Vegetation Index)
    
    NDVI = (NIR - Red) / (NIR + Red)
    
    Args:
        red_band: Red band array (0.65-0.68 μm)
        nir_band: Near-infrared band array (0.78-0.79 μm)
    
    Returns:
        NDVI array with values between -1 and 1
    """
    # Avoid division by zero
    denominator = (nir_band + red_band).astype(float)
    denominator[denominator == 0] = np.nan
    
    ndvi = (nir_band.astype(float) - red_band.astype(float)) / denominator
    
    # Clip values to valid range [-1, 1]
    ndvi = np.clip(ndvi, -1, 1)
    
    return ndvi

def calculate_ndvi_change(ndvi_before: np.ndarray, ndvi_after: np.ndarray) -> np.ndarray:
    """
    Calculate NDVI change between two time periods
    
    Args:
        ndvi_before: NDVI array from earlier time period
        ndvi_after: NDVI array from later time period
    
    Returns:
        Change array (negative values indicate vegetation loss)
    """
    return ndvi_after - ndvi_before

def validate_bbox(bbox: List[float]) -> bool:
    """
    Validate bounding box coordinates
    
    Args:
        bbox: List of 4 floats [min_lon, min_lat, max_lon, max_lat]
    
    Returns:
        True if valid, raises ValueError if invalid
    """
    if len(bbox) != 4:
        raise ValueError("Bounding box must contain exactly 4 values")
    
    min_lon, min_lat, max_lon, max_lat = bbox
    
    if min_lon >= max_lon:
        raise ValueError("min_lon must be less than max_lon")
    
    if min_lat >= max_lat:
        raise ValueError("min_lat must be less than max_lat")
    
    if not (-180 <= min_lon <= 180 and -180 <= max_lon <= 180):
        raise ValueError("Longitude must be between -180 and 180")
    
    if not (-90 <= min_lat <= 90 and -90 <= max_lat <= 90):
        raise ValueError("Latitude must be between -90 and 90")
    
    return True

