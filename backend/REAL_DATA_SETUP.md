# Real Satellite Data Setup

The application now **prioritizes real satellite data** from Microsoft Planetary Computer (FREE, no API key needed).

## What Data Sources Are Used

### ✅ Sentinel-2 (NDVI/Deforestation)
- Source: Planetary Computer
- Collection: `sentinel-2-l2a` (Level 2A - Surface Reflectance)
- Bands: B04 (Red), B08 (NIR)
- Cloud cover: Prefers <50%, searches ±5 days for best match

### ✅ Sentinel-1 (Flood Detection)
- Source: Planetary Computer  
- Collection: `sentinel-1-grd` (Ground Range Detected)
- Bands: VV, VH polarizations
- Date range: Searches ±7 days for nearest acquisition

### ✅ DEM (Afforestation)
- Primary: Copernicus DEM via Planetary Computer
- Fallback: Local DEM files in `data/inputs/`
- Last resort: Synthetic DEM

## Installation

Make sure these packages are installed:

```powershell
pip install pystac-client rioxarray xarray planetary-computer
```

## How It Works

1. **Real Data First**: Always tries to fetch real satellite data
2. **Date Flexibility**: If exact date not found, searches nearby dates (±3-7 days)
3. **Cloud Cover Handling**: For Sentinel-2, prefers images with <50% cloud cover
4. **Automatic Normalization**: Handles data scaling (uint16 → float, dB → linear)

## Status Messages

You'll see in the console:
- `✅ Using REAL Sentinel-2 data for 2023-06-15` - Real data found!
- `✅ Using REAL Sentinel-2 data from nearby date: 2023-06-18` - Using nearby date
- `⚠️ No real data found near 2023-06-15, using mock data` - Fallback to mock

## Troubleshooting

### "No real data found"
- **Date**: Satellite might not have coverage for that exact date
- **Location**: Some areas have sparse coverage
- **Solution**: Try different dates or locations known to have good coverage

### Slow Loading
- First-time data fetch can take 30-60 seconds
- Planetary Computer downloads data on-demand
- Subsequent requests for same area/date are cached

### Import Errors
```powershell
pip install --upgrade pystac-client rioxarray xarray planetary-computer
```

## Best Practices

1. **Use Recent Dates**: Better coverage for recent dates (2020-present)
2. **Reasonable AOI Size**: Keep bounding boxes under 1° x 1° for faster processing
3. **Check Coverage**: Visit https://planetarycomputer.microsoft.com/ to explore data availability

## Data Coverage

- **Sentinel-2**: Global coverage, revisit every 5 days
- **Sentinel-1**: Global coverage, revisit every 6-12 days (depends on location)
- **Copernicus DEM**: Global 30m resolution

---

**All data is FREE and requires no API key!** 🎉

