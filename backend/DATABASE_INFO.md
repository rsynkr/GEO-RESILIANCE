# Database Setup (OPTIONAL)

The database is **completely optional**. The application works perfectly without it.

## Current Behavior

The app will:
- ✅ Work perfectly without a database
- ✅ Return results directly to the frontend
- ✅ Show all analysis results on the map
- ✅ Function with all features

The database is **only used** for:
- Storing analysis results for later retrieval
- Building historical analysis dashboards
- Persisting results across sessions

## If You Want to Use Database

### Option 1: Disable Database (Recommended)

The database is already disabled by default. No action needed!

### Option 2: Enable and Configure Database

1. **Install PostgreSQL + PostGIS**:
   - Download from: https://www.postgresql.org/download/
   - Install PostGIS extension during installation

2. **Create Database**:
   ```sql
   CREATE DATABASE geo_resilience;
   \c geo_resilience
   CREATE EXTENSION postgis;
   ```

3. **Update Configuration**:
   Edit `backend/core/config.py` or create `.env` file:
   ```env
   USE_DATABASE=true
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=geo_resilience
   DB_USER=postgres
   DB_PASSWORD=your_password
   ```

4. **Restart Backend**

## Current Status

**Database is DISABLED by default** - you won't see any warnings.

The warning you saw is harmless and the app continues to work perfectly.

