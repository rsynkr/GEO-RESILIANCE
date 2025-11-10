# Windows Installation Guide

Installing geospatial libraries on Windows can be tricky due to GDAL dependencies. Follow these steps:

## Option 1: Easy Method (Recommended)

### Step 1: Install GDAL

Try this first:

```powershell
pip install gdal
```

If that fails, try installing from a wheel:

```powershell
# Download GDAL wheel from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal
# Or use pipwin to install pre-built wheels
pip install pipwin
pipwin install gdal
```

### Step 2: Install Geospatial Libraries

```powershell
pip install rasterio geopandas fiona pyproj
```

### Step 3: Install Other Dependencies

```powershell
pip install -r requirements_windows.txt
```

## Option 2: Using Conda (Alternative)

If you have Anaconda/Miniconda installed:

```powershell
conda install -c conda-forge gdal rasterio geopandas fiona pyproj
pip install -r requirements_windows.txt
```

## Option 3: Minimal Installation (Skip Geospatial Libraries)

If you just want to test the API without the full geospatial stack, you can install minimal requirements:

```powershell
pip install fastapi uvicorn[standard] pydantic pydantic-settings numpy scipy pandas python-multipart python-dotenv
```

**Note**: The analysis modules will still work with mock data, but some functions may have reduced functionality.

## Troubleshooting GDAL Installation

### Error: "ERROR: A GDAL API version must be specified"

**Solution 1**: Install GDAL using pipwin
```powershell
pip install pipwin
pipwin install gdal
```

**Solution 2**: Download pre-built wheel manually
1. Go to: https://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal
2. Download the appropriate wheel for your Python version
3. Install: `pip install path/to/downloaded/gdal_wheel.whl`

**Solution 3**: Use OSGeo4W
1. Download OSGeo4W from: https://trac.osgeo.org/osgeo4w/
2. Install GDAL
3. Add to PATH or set GDAL_CONFIG environment variable

### Still Having Issues?

If GDAL installation continues to fail, you can still run the application with limited functionality:

```powershell
# Install core dependencies only
pip install fastapi uvicorn[standard] pydantic pydantic-settings numpy scipy shapely geopandas python-multipart python-dotenv
```

The application will work, but some advanced raster processing features may be limited.


