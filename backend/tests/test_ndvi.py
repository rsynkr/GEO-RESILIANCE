"""
Tests for NDVI deforestation analysis module
"""

import pytest
from modules.ndvi_module import analyze_ndvi_deforestation

def test_ndvi_analysis_basic():
    """Test basic NDVI analysis with valid inputs"""
    bbox = [-122.5, 37.7, -122.3, 37.9]  # San Francisco Bay Area
    start_date = "2023-01-01"
    end_date = "2023-12-31"
    
    result = analyze_ndvi_deforestation(bbox, start_date, end_date)
    
    assert "area_km2" in result
    assert "geojson" in result
    assert result["area_km2"] >= 0
    assert result["geojson"]["type"] == "FeatureCollection"

def test_ndvi_analysis_invalid_bbox():
    """Test NDVI analysis with invalid bounding box"""
    bbox = [-122.5, 37.7, -122.3]  # Invalid: only 3 values
    start_date = "2023-01-01"
    end_date = "2023-12-31"
    
    with pytest.raises((ValueError, AssertionError)):
        analyze_ndvi_deforestation(bbox, start_date, end_date)

if __name__ == "__main__":
    pytest.main([__file__])

