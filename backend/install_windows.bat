@echo off
REM Windows installation script for Geo-Resilience backend
REM This handles GDAL installation on Windows

echo Installing Geo-Resilience backend dependencies...
echo.

REM Step 1: Install GDAL first (required for rasterio on Windows)
echo [1/3] Installing GDAL (this may take a few minutes)...
pip install gdal

REM Step 2: Install other geospatial dependencies that need GDAL
echo [2/3] Installing geospatial libraries...
pip install rasterio geopandas fiona pyproj

REM Step 3: Install remaining dependencies
echo [3/3] Installing other dependencies...
pip install -r requirements_windows.txt

echo.
echo Installation complete!
echo.
echo To start the server, run:
echo   uvicorn main:app --reload
pause


