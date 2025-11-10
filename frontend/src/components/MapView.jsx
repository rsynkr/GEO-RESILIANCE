import React, { useEffect, useRef } from 'react'
import { MapContainer, TileLayer, GeoJSON, useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import './MapView.css'

// Fix for default markers in Leaflet with React
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
})

// Component to update map bounds when layers change
function MapUpdater({ geojson }) {
  const map = useMap()

  useEffect(() => {
    if (geojson && geojson.features && geojson.features.length > 0) {
      const bounds = L.geoJSON(geojson).getBounds()
      if (bounds.isValid()) {
        map.fitBounds(bounds, { padding: [50, 50] })
      }
    }
  }, [geojson, map])

  return null
}

function MapView({ layers }) {
  const mapRef = useRef(null)

  // Default center (San Francisco Bay Area)
  const defaultCenter = [37.7749, -122.4194]
  const defaultZoom = 10

  const getStyleForLayer = (layerType) => {
    return (feature) => {
      const layer = layers[layerType]
      if (!layer || !layer.visible) {
        return { fillOpacity: 0, weight: 0 }
      }

      return {
        fillColor: layer.color,
        fillOpacity: 0.4,
        color: layer.color,
        weight: 2,
        opacity: 0.8
      }
    }
  }

  const onEachFeature = (feature, layer, layerType) => {
    // Add popup with area information
    if (feature.properties && feature.properties.area_km2) {
      const area = feature.properties.area_km2
      const analysisType = layerType === 'ndvi' ? 'Deforestation' :
                          layerType === 'flood' ? 'Flood Area' :
                          'Afforestation Zone'
      
      layer.bindPopup(`
        <div style="font-family: Arial, sans-serif;">
          <strong>${analysisType}</strong><br/>
          Area: ${area.toFixed(2)} km²
          ${feature.properties.ndvi_change !== undefined ? 
            `<br/>NDVI Change: ${feature.properties.ndvi_change.toFixed(3)}` : ''}
          ${feature.properties.backscatter_change !== undefined ? 
            `<br/>Backscatter Change: ${feature.properties.backscatter_change.toFixed(4)}` : ''}
        </div>
      `)
    }
    
    // Add hover effect
    layer.on({
      mouseover: (e) => {
        const layer = e.target
        layer.setStyle({
          fillOpacity: 0.6,
          weight: 3
        })
      },
      mouseout: (e) => {
        const layer = e.target
        layer.setStyle({
          fillOpacity: 0.4,
          weight: 2
        })
      }
    })
  }

  return (
    <div className="map-view">
      <MapContainer
        center={defaultCenter}
        zoom={defaultZoom}
        style={{ height: '100%', width: '100%' }}
        ref={mapRef}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* NDVI Layer */}
        {layers.ndvi.visible && layers.ndvi.data && (
          <>
            <GeoJSON
              data={layers.ndvi.data}
              style={getStyleForLayer('ndvi')}
              onEachFeature={(feature, layer) => onEachFeature(feature, layer, 'ndvi')}
            />
            <MapUpdater geojson={layers.ndvi.data} />
          </>
        )}

        {/* Flood Layer */}
        {layers.flood.visible && layers.flood.data && (
          <>
            <GeoJSON
              data={layers.flood.data}
              style={getStyleForLayer('flood')}
              onEachFeature={(feature, layer) => onEachFeature(feature, layer, 'flood')}
            />
            <MapUpdater geojson={layers.flood.data} />
          </>
        )}

        {/* Afforestation Layer */}
        {layers.afforestation.visible && layers.afforestation.data && (
          <>
            <GeoJSON
              data={layers.afforestation.data}
              style={getStyleForLayer('afforestation')}
              onEachFeature={(feature, layer) => onEachFeature(feature, layer, 'afforestation')}
            />
            <MapUpdater geojson={layers.afforestation.data} />
          </>
        )}
      </MapContainer>
    </div>
  )
}

export default MapView

