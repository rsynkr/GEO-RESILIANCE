# Installing Real Satellite Data Support

The application now supports fetching **real satellite data** from Microsoft Planetary Computer (FREE, no API key required).

## Quick Install

After installing the basic requirements, install the satellite data packages:

```powershell
pip install pystac-client rioxarray xarray planetary-computer
```

## What This Enables

- **Real Sentinel-2 data** for NDVI/deforestation analysis
- **Real Sentinel-1 SAR data** for flood detection
- **Free access** through Microsoft Planetary Computer
- **Automatic fallback** to mock data if real data unavailable

## How It Works

1. When you run an analysis, it first tries to fetch real data from Planetary Computer
2. If real data is found, it uses that
3. If not found (e.g., no coverage for that date/location), it falls back to mock data
4. You'll see messages in the console indicating which data source is used

## Example Output

```
✅ Using REAL Sentinel-2 data for 2023-06-15
```

or

```
⚠️ No real data found for 2023-06-15, using mock data
```

## Troubleshooting

### Import Errors

If you get import errors for `pystac_client`, `rioxarray`, etc.:

```powershell
pip install --upgrade pystac-client rioxarray xarray planetary-computer
```

### No Real Data Found

This can happen if:
- The date has no satellite coverage
- The area is outside Sentinel coverage zones
- Cloud cover is too high

The app will automatically use mock data in these cases.

### Network Issues

Planetary Computer requires internet access. Make sure you have a stable connection.

## Alternative Data Sources

If you want to use other data sources:

1. **Sentinel Hub**: Requires API key (free tier available)
2. **Copernicus Open Access Hub**: Free but requires account registration
3. **Local files**: Place satellite data in `data/inputs/` folder

See the module files for integration examples.


