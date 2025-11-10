@echo off
REM Quick dependency installer for backend

title Installing Backend Dependencies
color 0B

echo.
echo ========================================
echo   Installing Backend Dependencies
echo ========================================
echo.

REM Activate venv if not already activated
if not exist "venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat

echo Upgrading pip...
python -m pip install --upgrade pip --quiet

echo.
echo Installing core dependencies (this may take a few minutes)...
echo.

REM Install core packages first
pip install fastapi uvicorn[standard] pydantic pydantic-settings python-multipart python-dotenv

echo.
echo Installing database packages...
pip install sqlalchemy psycopg2-binary geoalchemy2

echo.
echo Installing scientific computing packages...
pip install numpy scipy pandas shapely

echo.
echo Attempting to install geospatial packages...
pip install geopandas --quiet 2>nul
if errorlevel 1 (
    echo [WARNING] geopandas installation had issues, but continuing...
)

REM Try satellite data packages
echo.
echo Installing satellite data packages...
pip install pystac-client xarray planetary-computer --quiet 2>nul

REM Try rioxarray (may fail on Windows)
pip install rioxarray --quiet 2>nul
if errorlevel 1 (
    echo [WARNING] rioxarray skipped - app will use mock data
)

REM Try rasterio (often fails on Windows due to GDAL)
pip install rasterio --quiet 2>nul
if errorlevel 1 (
    echo [WARNING] rasterio skipped - app will use alternative methods
)

echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo You can now start the server with:
echo   uvicorn main:app --reload
echo.
pause

