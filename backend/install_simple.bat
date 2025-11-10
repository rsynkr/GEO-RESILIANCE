@echo off
echo Installing Geo-Resilience backend (simplified for Windows)
echo.

REM First, try to install GDAL - this might work or might need manual intervention
echo Installing GDAL...
pip install gdal
if errorlevel 1 (
    echo.
    echo GDAL installation failed. Trying alternative method...
    pip install pipwin
    pipwin install gdal
)

echo.
echo Installing geospatial libraries...
pip install rasterio geopandas fiona pyproj

echo.
echo Installing other dependencies...
pip install fastapi uvicorn[standard] pydantic pydantic-settings numpy scipy pandas shapely python-multipart python-dotenv

echo.
echo Installation attempt complete!
echo If you see errors, try the manual installation steps in INSTALL_WINDOWS.md
pause


