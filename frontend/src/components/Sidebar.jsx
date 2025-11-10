import React, { useState } from 'react'
import { runAnalysis } from '../services/api'
import './Sidebar.css'

function Sidebar({ onAnalysisResult, loading, setLoading, error, setError }) {
  const [bbox, setBbox] = useState({
    minLon: '-122.5',
    minLat: '37.7',
    maxLon: '-122.3',
    maxLat: '37.9'
  })
  
  const [startDate, setStartDate] = useState('2023-01-01')
  const [endDate, setEndDate] = useState('2023-12-31')
  const [analysisType, setAnalysisType] = useState('ndvi')

  const handleRunAnalysis = async () => {
    setLoading(true)
    setError(null)

    try {
      // Validate bounding box
      const bboxArray = [
        parseFloat(bbox.minLon),
        parseFloat(bbox.minLat),
        parseFloat(bbox.maxLon),
        parseFloat(bbox.maxLat)
      ]

      if (bboxArray.some(isNaN)) {
        throw new Error('Please enter valid coordinates for bounding box')
      }

      if (bboxArray[0] >= bboxArray[2] || bboxArray[1] >= bboxArray[3]) {
        throw new Error('Invalid bounding box: min values must be less than max values')
      }

      // Validate dates
      if (!startDate || !endDate) {
        throw new Error('Please select both start and end dates')
      }

      const result = await runAnalysis(analysisType, bboxArray, startDate, endDate)
      onAnalysisResult(analysisType, result)
    } catch (err) {
      setError(err.message || 'Analysis failed. Please check your inputs and try again.')
      console.error('Analysis error:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="sidebar">
      <div className="sidebar-content">
        <h2>Analysis Configuration</h2>

        <div className="form-group">
          <label htmlFor="analysis-type">Analysis Type</label>
          <select
            id="analysis-type"
            value={analysisType}
            onChange={(e) => setAnalysisType(e.target.value)}
            className="form-control"
          >
            <option value="ndvi">🟢 NDVI & Deforestation</option>
            <option value="flood">🔵 Flood Detection (SAR)</option>
            <option value="afforestation">🌲 Afforestation Suitability</option>
          </select>
          <small className="form-help">
            {analysisType === 'ndvi' && 'Detects deforestation using NDVI changes from Sentinel-2'}
            {analysisType === 'flood' && 'Maps flooded areas using Sentinel-1 SAR data'}
            {analysisType === 'afforestation' && 'Identifies suitable zones for tree planting'}
          </small>
        </div>

        <div className="form-group">
          <label>Bounding Box (WGS84)</label>
          <div className="bbox-inputs">
            <div className="bbox-row">
              <input
                type="number"
                placeholder="Min Longitude"
                value={bbox.minLon}
                onChange={(e) => setBbox({ ...bbox, minLon: e.target.value })}
                className="form-control"
                step="0.0001"
              />
              <input
                type="number"
                placeholder="Min Latitude"
                value={bbox.minLat}
                onChange={(e) => setBbox({ ...bbox, minLat: e.target.value })}
                className="form-control"
                step="0.0001"
              />
            </div>
            <div className="bbox-row">
              <input
                type="number"
                placeholder="Max Longitude"
                value={bbox.maxLon}
                onChange={(e) => setBbox({ ...bbox, maxLon: e.target.value })}
                className="form-control"
                step="0.0001"
              />
              <input
                type="number"
                placeholder="Max Latitude"
                value={bbox.maxLat}
                onChange={(e) => setBbox({ ...bbox, maxLat: e.target.value })}
                className="form-control"
                step="0.0001"
              />
            </div>
          </div>
          <small className="form-help">
            Format: [min_lon, min_lat, max_lon, max_lat]
          </small>
        </div>

        <div className="form-group">
          <label htmlFor="start-date">Start Date</label>
          <input
            id="start-date"
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            className="form-control"
          />
        </div>

        <div className="form-group">
          <label htmlFor="end-date">End Date</label>
          <input
            id="end-date"
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            className="form-control"
          />
        </div>

        <button
          onClick={handleRunAnalysis}
          disabled={loading}
          className="btn-primary"
        >
          {loading ? 'Running Analysis...' : '🚀 Run Analysis'}
        </button>

        <div className="sidebar-info">
          <h3>Quick Tips</h3>
          <ul>
            <li>Use coordinates in decimal degrees (WGS84)</li>
            <li>Keep AOI under ~100 km² for faster processing</li>
            <li>Date range affects temporal change detection</li>
            <li>Results appear as colored polygons on the map</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

export default Sidebar

