import React, { useState, useEffect } from 'react'
import MapView from './components/MapView'
import Sidebar from './components/Sidebar'
import LayerToggle from './components/LayerToggle'
import { checkHealth } from './services/api'
import './App.css'

function App() {
  const [layers, setLayers] = useState({
    ndvi: { visible: false, data: null, color: '#ff0000' },      // Red for deforestation
    flood: { visible: false, data: null, color: '#0066ff' },     // Blue for flood
    afforestation: { visible: false, data: null, color: '#00aa00' } // Green for afforestation
  })

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [backendStatus, setBackendStatus] = useState('checking')

  // Check backend health on mount
  useEffect(() => {
    checkBackendHealth()
  }, [])

  const checkBackendHealth = async () => {
    try {
      await checkHealth()
      setBackendStatus('online')
      setError(null)
    } catch (err) {
      setBackendStatus('offline')
      setError('Backend server is not running. Please start it first!')
    }
  }

  const handleAnalysisResult = (type, result) => {
    setLayers(prev => ({
      ...prev,
      [type]: {
        ...prev[type],
        visible: true,
        data: result.geojson,
        area: result.area_km2
      }
    }))
    setError(null)
  }

  const toggleLayer = (layerType) => {
    setLayers(prev => ({
      ...prev,
      [layerType]: {
        ...prev[layerType],
        visible: !prev[layerType].visible
      }
    }))
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>🛰️ Geo-Resilience Initiative</h1>
        <p>Geospatial Intelligence Platform for Environmental Monitoring</p>
      </header>
      
      <div className="app-container">
        <Sidebar 
          onAnalysisResult={handleAnalysisResult}
          loading={loading}
          setLoading={setLoading}
          error={error}
          setError={setError}
        />
        
        <div className="map-container">
          <LayerToggle layers={layers} onToggle={toggleLayer} />
          <MapView layers={layers} />
        </div>
      </div>

      {error && (
        <div className="error-banner">
          {error}
          {backendStatus === 'offline' && (
            <div style={{ marginTop: '10px', fontSize: '0.9em' }}>
              <strong>How to fix:</strong><br/>
              1. Make sure the "Geo-Resilience Backend" window is open<br/>
              2. Check that it shows "Uvicorn running on http://127.0.0.1:8000"<br/>
              3. Try refreshing this page
            </div>
          )}
        </div>
      )}
      
      {backendStatus === 'checking' && (
        <div className="info-banner">
          Checking backend connection...
        </div>
      )}
      
      {backendStatus === 'online' && error && error.includes('Unable to reach') && (
        <div className="warning-banner">
          Backend is running but request timed out. Try again in a moment.
        </div>
      )}
    </div>
  )
}

export default App

