# Geo-Resilience Initiative - Backend

FastAPI backend for geospatial intelligence platform analyzing wildfires, floods, and afforestation suitability.

## Features

- **NDVI Analysis**: Detects deforestation using Sentinel-2 NDVI changes
- **Flood Detection**: Uses Sentinel-1 SAR data for flood mapping
- **Afforestation Suitability**: Identifies suitable zones using DEM and OSM data

## Setup

### Prerequisites

- Python 3.10+
- PostgreSQL 15+ with PostGIS extension
- pip

### Installation

1. **Create and activate virtual environment**:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure PostgreSQL/PostGIS**:
   - Install PostgreSQL 15+ from https://www.postgresql.org/download/
   - Install PostGIS extension:
```sql
CREATE DATABASE geo_resilience;
\c geo_resilience
CREATE EXTENSION postgis;
```

4. **Set environment variables** (create `.env` file):
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=geo_resilience
DB_USER=postgres
DB_PASSWORD=your_password
```

### Running the Server

```bash
# Development mode with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or use Python directly
python main.py
```

The API will be available at `http://localhost:8000`

### API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### POST `/analyze/ndvi`
NDVI and deforestation analysis

**Request Body**:
```json
{
  "bbox": [-122.5, 37.7, -122.3, 37.9],
  "start_date": "2023-01-01",
  "end_date": "2023-12-31"
}
```

**Response**:
```json
{
  "status": "success",
  "type": "ndvi",
  "area_km2": 12.34,
  "geojson": {...},
  "metadata": {...}
}
```

### POST `/analyze/flood`
SAR flood detection

Same request/response format as NDVI endpoint.

### POST `/analyze/afforestation`
Afforestation suitability analysis

Same request/response format as NDVI endpoint.

## Project Structure

```
backend/
├── main.py                 # FastAPI entry point
├── core/
│   ├── config.py          # Configuration and settings
│   └── utils.py           # Shared geospatial utilities
├── modules/
│   ├── ndvi_module.py     # NDVI analysis
│   ├── sar_module.py      # SAR flood detection
│   └── afforestation_module.py  # Afforestation suitability
├── database/
│   ├── db_config.py       # Database connection
│   └── models.py          # SQLAlchemy models
└── tests/                 # Unit tests
```

## Notes

- Current implementation uses **placeholder/mock data** for satellite imagery
- To integrate real data, update `fetch_sentinel2_data()` and `fetch_sentinel1_sar()` functions
- Recommended services: Sentinel Hub API, Planetary Computer, Copernicus Open Access Hub
- Database integration is optional - API works without PostgreSQL for testing

## Testing

```bash
pytest tests/
```

## License

MIT

