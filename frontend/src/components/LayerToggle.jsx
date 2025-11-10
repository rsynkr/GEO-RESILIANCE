import React from 'react'
import './LayerToggle.css'

function LayerToggle({ layers, onToggle }) {
  return (
    <div className="layer-toggle">
      <h3>Layers</h3>
      <div className="layer-list">
        <label className="layer-item">
          <input
            type="checkbox"
            checked={layers.ndvi.visible}
            onChange={() => onToggle('ndvi')}
          />
          <span className="layer-color" style={{ backgroundColor: layers.ndvi.color }}></span>
          <span className="layer-label">Deforestation</span>
          {layers.ndvi.data && (
            <span className="layer-area">
              {layers.ndvi.area ? `${layers.ndvi.area.toFixed(2)} km²` : ''}
            </span>
          )}
        </label>

        <label className="layer-item">
          <input
            type="checkbox"
            checked={layers.flood.visible}
            onChange={() => onToggle('flood')}
          />
          <span className="layer-color" style={{ backgroundColor: layers.flood.color }}></span>
          <span className="layer-label">Flood</span>
          {layers.flood.data && (
            <span className="layer-area">
              {layers.flood.area ? `${layers.flood.area.toFixed(2)} km²` : ''}
            </span>
          )}
        </label>

        <label className="layer-item">
          <input
            type="checkbox"
            checked={layers.afforestation.visible}
            onChange={() => onToggle('afforestation')}
          />
          <span className="layer-color" style={{ backgroundColor: layers.afforestation.color }}></span>
          <span className="layer-label">Afforestation</span>
          {layers.afforestation.data && (
            <span className="layer-area">
              {layers.afforestation.area ? `${layers.afforestation.area.toFixed(2)} km²` : ''}
            </span>
          )}
        </label>
      </div>
    </div>
  )
}

export default LayerToggle

