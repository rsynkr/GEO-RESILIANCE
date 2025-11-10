"""
Real Satellite Data Fetcher
Uses Microsoft Planetary Computer to fetch Sentinel-2 and Sentinel-1 data
Free, no API key required for basic use
"""

import numpy as np
import geopandas as gpd
from shapely.geometry import box
from typing import List, Dict, Optional
from datetime import datetime
import requests
import os

try:
    import rioxarray
    import xarray as xr
    from pystac_client import Client
    import planetary_computer as pc
    REAL_DATA_AVAILABLE = True
except ImportError:
    REAL_DATA_AVAILABLE = False
    print("Warning: pystac-client, rioxarray, or planetary-computer not installed.")
    print("Install with: pip install pystac-client rioxarray planetary-computer")
    print("Using mock data as fallback.")

def fetch_sentinel2_real(bbox: List[float], date: str) -> Optional[Dict[str, np.ndarray]]:
    """
    Fetch real Sentinel-2 data from Planetary Computer
    
    Args:
        bbox: Bounding box [min_lon, min_lat, max_lon, max_lat]
        date: Date string in YYYY-MM-DD format
    
    Returns:
        Dictionary with 'red' and 'nir' bands as numpy arrays, or None if failed
    """
    if not REAL_DATA_AVAILABLE:
        return None
    
    try:
        # Create bounding box geometry
        min_lon, min_lat, max_lon, max_lat = bbox
        bbox_geom = box(min_lon, min_lat, max_lon, max_lat)
        
        # Parse date
        from datetime import timedelta
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        
        # Connect to Planetary Computer STAC catalog
        catalog = Client.open("https://planetarycomputer.microsoft.com/api/stac/v1")
        
        # Search for Sentinel-2 L2A products with date range tolerance
        date_start = date_obj - timedelta(days=5)  # Search 5 days before
        date_end = date_obj + timedelta(days=5)    # Search 5 days after
        
        search = catalog.search(
            collections=["sentinel-2-l2a"],
            bbox=[min_lon, min_lat, max_lon, max_lat],
            datetime=f"{date_start.strftime('%Y-%m-%d')}T00:00:00Z/{date_end.strftime('%Y-%m-%d')}T23:59:59Z",
            limit=10,  # Get more options to find best match
            query={"eo:cloud_cover": {"lt": 50}}  # Accept up to 50% cloud cover
        )
        
        items = list(search.items())
        
        if not items:
            print(f"No Sentinel-2 data found near {date}, trying broader search...")
            # Try without cloud cover filter
            search = catalog.search(
                collections=["sentinel-2-l2a"],
                bbox=[min_lon, min_lat, max_lon, max_lat],
                datetime=f"{date_start.strftime('%Y-%m-%d')}T00:00:00Z/{date_end.strftime('%Y-%m-%d')}T23:59:59Z",
                limit=10
            )
            items = list(search.items())
        
        if not items:
            print(f"⚠️ No Sentinel-2 data found for area near {date}")
            return None
        
        # Sort by cloud cover and date proximity
        def sort_key(item):
            cloud_cover = item.properties.get("eo:cloud_cover", 100)
            item_date = datetime.fromisoformat(item.properties["datetime"].replace("Z", "+00:00"))
            date_diff = abs((item_date.date() - date_obj.date()).days)
            return (cloud_cover, date_diff)
        
        items.sort(key=sort_key)
        
        # Get the first item
        item = items[0]
        
        # Sign the item with Planetary Computer token
        signed_item = pc.sign(item)
        
        # Get red (B04) and NIR (B08) bands
        red_asset = signed_item.assets.get("B04")  # Red band
        nir_asset = signed_item.assets.get("B08")   # NIR band
        
        if not red_asset or not nir_asset:
            return None
        
        # Load bands using rioxarray
        print(f"Loading Sentinel-2 bands from {item.id}...")
        red_ds = rioxarray.open_rasterio(red_asset.href, chunks="auto")
        nir_ds = rioxarray.open_rasterio(nir_asset.href, chunks="auto")
        
        # Clip to bounding box
        red_clipped = red_ds.rio.clip_box(minx=min_lon, miny=min_lat, maxx=max_lon, maxy=max_lat)
        nir_clipped = nir_ds.rio.clip_box(minx=min_lon, miny=min_lat, maxx=max_lon, maxy=max_lat)
        
        # Convert to numpy arrays (take first band if multi-band)
        red_array = red_clipped.values
        nir_array = nir_clipped.values
        
        if red_array.ndim > 2:
            red_array = red_array[0]  # Take first band
        if nir_array.ndim > 2:
            nir_array = nir_array[0]
        
        # Normalize Sentinel-2 data (typically stored as uint16, scale to 0-1)
        # Sentinel-2 L2A reflectance values are typically 0-10000 (divide by 10000)
        if red_array.dtype == np.uint16 or np.max(red_array) > 1.0:
            red_array = red_array.astype(np.float32) / 10000.0
            nir_array = nir_array.astype(np.float32) / 10000.0
            print(f"Normalized Sentinel-2 reflectance values")
        
        print(f"Successfully loaded real Sentinel-2 data: {red_array.shape}")
        
        # Get transform and CRS
        transform = red_clipped.rio.transform()
        crs = str(red_clipped.rio.crs)
        
        return {
            "red": red_array,
            "nir": nir_array,
            "transform": transform,
            "crs": crs
        }
    
    except Exception as e:
        print(f"Error fetching real Sentinel-2 data: {e}")
        return None

def fetch_sentinel1_real(bbox: List[float], date: str) -> Optional[Dict[str, np.ndarray]]:
    """
    Fetch real Sentinel-1 SAR data from Planetary Computer
    
    Args:
        bbox: Bounding box [min_lon, min_lat, max_lon, max_lat]
        date: Date string in YYYY-MM-DD format
    
    Returns:
        Dictionary with 'vv' and 'vh' bands as numpy arrays, or None if failed
    """
    if not REAL_DATA_AVAILABLE:
        return None
    
    try:
        min_lon, min_lat, max_lon, max_lat = bbox
        
        # Connect to Planetary Computer STAC catalog
        catalog = Client.open("https://planetarycomputer.microsoft.com/api/stac/v1")
        
        # Search for Sentinel-1 GRD products with date range
        from datetime import timedelta
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        date_start = date_obj - timedelta(days=7)  # Search 7 days before
        date_end = date_obj + timedelta(days=7)    # Search 7 days after
        
        search = catalog.search(
            collections=["sentinel-1-grd"],
            bbox=[min_lon, min_lat, max_lon, max_lat],
            datetime=f"{date_start.strftime('%Y-%m-%d')}T00:00:00Z/{date_end.strftime('%Y-%m-%d')}T23:59:59Z",
            limit=10
        )
        
        items = list(search.items())
        
        if not items:
            print(f"⚠️ No Sentinel-1 data found for area near {date}")
            return None
        
        # Sort by date proximity
        def sort_key(item):
            item_date = datetime.fromisoformat(item.properties["datetime"].replace("Z", "+00:00"))
            date_diff = abs((item_date.date() - date_obj.date()).days)
            return date_diff
        
        items.sort(key=sort_key)
        
        # Get the first item
        item = items[0]
        signed_item = pc.sign(item)
        
        # Get VV and VH bands - try multiple asset name variations
        vv_asset = signed_item.assets.get("vv") or signed_item.assets.get("VV")
        vh_asset = signed_item.assets.get("vh") or signed_item.assets.get("VH")
        
        # Try gamma0 naming convention
        if not vv_asset:
            vv_asset = signed_item.assets.get("gamma0-vv") or signed_item.assets.get("gamma0-VV")
        if not vh_asset:
            vh_asset = signed_item.assets.get("gamma0-vh") or signed_item.assets.get("gamma0-VH")
        
        if not vv_asset or not vh_asset:
            return None
        
        # Load bands
        print(f"Loading Sentinel-1 bands from {item.id}...")
        vv_ds = rioxarray.open_rasterio(vv_asset.href, chunks="auto")
        vh_ds = rioxarray.open_rasterio(vh_asset.href, chunks="auto")
        
        # Clip to bounding box
        vv_clipped = vv_ds.rio.clip_box(minx=min_lon, miny=min_lat, maxx=max_lon, maxy=max_lat)
        vh_clipped = vh_ds.rio.clip_box(minx=min_lon, miny=min_lat, maxx=max_lon, maxy=max_lat)
        
        # Convert to numpy arrays
        vv_array = vv_clipped.values
        vh_array = vh_clipped.values
        
        if vv_array.ndim > 2:
            vv_array = vv_array[0]
        if vh_array.ndim > 2:
            vh_array = vh_array[0]
        
        # Convert from dB to linear scale if needed (SAR data is often in dB)
        # If values are negative (typical for dB), convert: linear = 10^(dB/10)
        if np.any(vv_array < 0):
            vv_array = np.power(10, vv_array / 10.0)
            vh_array = np.power(10, vh_array / 10.0)
            print(f"Converted SAR data from dB to linear scale")
        
        print(f"Successfully loaded real Sentinel-1 data: {vv_array.shape}")
        
        # Get transform and CRS
        transform = vv_clipped.rio.transform()
        crs = str(vv_clipped.rio.crs)
        
        return {
            "vv": vv_array,
            "vh": vh_array,
            "transform": transform,
            "crs": crs
        }
    
    except Exception as e:
        print(f"Error fetching real Sentinel-1 data: {e}")
        return None


