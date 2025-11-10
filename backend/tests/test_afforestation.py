"""
Tests for afforestation suitability module
"""

import pytest
from modules.afforestation_module import analyze_afforestation_suitability

def test_afforestation_analysis_basic():
    """Test basic afforestation analysis with valid inputs"""
    bbox = [-122.5, 37.7, -122.3, 37.9]  # San Francisco Bay Area
    start_date = "2023-01-01"
    end_date = "2023-12-31"
    
    result = analyze_afforestation_suitability(bbox, start_date, end_date)
    
    assert "area_km2" in result
    assert "geojson" in result
    assert result["area_km2"] >= 0
    assert result["geojson"]["type"] == "FeatureCollection"

def test_afforestation_analysis_invalid_bbox():
    """Test afforestation analysis with invalid bounding box"""
    bbox = [-122.5, 37.7]  # Invalid: only 2 values
    start_date = "2023-01-01"
    end_date = "2023-12-31"
    
    with pytest.raises((ValueError, AssertionError)):
        analyze_afforestation_suitability(bbox, start_date, end_date)

if __name__ == "__main__":
    pytest.main([__file__])

