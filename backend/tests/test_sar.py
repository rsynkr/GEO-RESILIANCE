"""
Tests for SAR flood detection module
"""

import pytest
from modules.sar_module import analyze_flood_sar

def test_sar_analysis_basic():
    """Test basic SAR flood analysis with valid inputs"""
    bbox = [-122.5, 37.7, -122.3, 37.9]  # San Francisco Bay Area
    start_date = "2023-01-01"
    end_date = "2023-12-31"
    
    result = analyze_flood_sar(bbox, start_date, end_date)
    
    assert "area_km2" in result
    assert "geojson" in result
    assert result["area_km2"] >= 0
    assert result["geojson"]["type"] == "FeatureCollection"

def test_sar_analysis_invalid_bbox():
    """Test SAR analysis with invalid bounding box"""
    bbox = [-122.5]  # Invalid: only 1 value
    start_date = "2023-01-01"
    end_date = "2023-12-31"
    
    with pytest.raises((ValueError, AssertionError)):
        analyze_flood_sar(bbox, start_date, end_date)

if __name__ == "__main__":
    pytest.main([__file__])

