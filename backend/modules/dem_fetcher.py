"""
DEM (Digital Elevation Model) Data Fetcher
Fetches real DEM data from various sources
"""

import numpy as np
from typing import List, Dict, Optional
import os

try:
    import rioxarray
    from pystac_client import Client
    import planetary_computer as pc
    DEM_REAL_AVAILABLE = True
except ImportError:
    DEM_REAL_AVAILABLE = False
    print("Warning: rioxarray or planetary-computer not available for DEM fetching")

def fetch_dem_real(bbox: List[float]) -> Optional[Dict[str, np.ndarray]]:
    """
    Fetch real DEM data from Copernicus DEM or other sources via Planetary Computer
    
    Args:
        bbox: Bounding box [min_lon, min_lat, max_lon, max_lat]
    
    Returns:
        Dictionary with 'elevation' array and metadata, or None if failed
    """
    if not DEM_REAL_AVAILABLE:
        return None
    
    try:
        min_lon, min_lat, max_lon, max_lat = bbox
        
        # Connect to Planetary Computer
        catalog = Client.open("https://planetarycomputer.microsoft.com/api/stac/v1")
        
        # Try Copernicus DEM 30m
        try:
            search = catalog.search(
                collections=["copernicus-dem"],
                bbox=[min_lon, min_lat, max_lon, max_lat],
                limit=1
            )
            items = list(search.items())
            
            if items:
                item = items[0]
                signed_item = pc.sign(item)
                
                # Get DEM asset
                dem_asset = signed_item.assets.get("data")
                if not dem_asset:
                    dem_asset = signed_item.assets.get("dem")
                
                if dem_asset:
                    # Load DEM
                    dem_ds = rioxarray.open_rasterio(dem_asset.href, chunks="auto")
                    dem_clipped = dem_ds.rio.clip_box(minx=min_lon, miny=min_lat, maxx=max_lon, maxy=max_lat)
                    
                    elevation = dem_clipped.values
                    if elevation.ndim > 2:
                        elevation = elevation[0]
                    
                    return {
                        "elevation": elevation,
                        "transform": dem_clipped.rio.transform(),
                        "crs": str(dem_clipped.rio.crs)
                    }
        except Exception as e:
            print(f"Copernicus DEM fetch failed: {e}")
        
        # Fallback to NASADEM or SRTM if available
        # (Planetary Computer may have these)
        
    except Exception as e:
        print(f"Error fetching real DEM: {e}")
    
    return None

