/**
 * API service for communicating with FastAPI backend
 */

import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  },
  timeout: 30000 // 30 second timeout
})

/**
 * Run geospatial analysis
 * 
 * @param {string} analysisType - 'ndvi', 'flood', or 'afforestation'
 * @param {number[]} bbox - Bounding box [min_lon, min_lat, max_lon, max_lat]
 * @param {string} startDate - Start date in YYYY-MM-DD format
 * @param {string} endDate - End date in YYYY-MM-DD format
 * @returns {Promise<Object>} Analysis result with geojson and area_km2
 */
export async function runAnalysis(analysisType, bbox, startDate, endDate) {
  try {
    const endpoint = `/analyze/${analysisType}`
    
    const response = await api.post(endpoint, {
      bbox,
      start_date: startDate,
      end_date: endDate
    })
    
    if (response.data.status === 'success') {
      return response.data
    } else {
      throw new Error(response.data.detail || 'Analysis failed')
    }
  } catch (error) {
    if (error.response) {
      // Server responded with error status
      throw new Error(error.response.data.detail || `Server error: ${error.response.status}`)
    } else if (error.request) {
      // Request made but no response
      throw new Error('Unable to reach server. Please ensure the backend is running on http://localhost:8000')
    } else {
      // Error in request setup
      throw new Error(error.message || 'An unexpected error occurred')
    }
  }
}

/**
 * Health check for API
 */
export async function checkHealth() {
  try {
    const response = await api.get('/health')
    return response.data
  } catch (error) {
    throw new Error('Backend is not available')
  }
}

export default api

