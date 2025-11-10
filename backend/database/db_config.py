"""
Database configuration for PostgreSQL/PostGIS
SQLAlchemy setup and connection management

NOTE: Database is OPTIONAL. The app works perfectly without it.
Results are returned directly to the frontend without needing database storage.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from core.config import settings

# Create SQLAlchemy engine with PostGIS support (only if database is enabled)
# Use a dummy URL if database is disabled to avoid connection attempts
if settings.USE_DATABASE and settings.DATABASE_URL:
    engine = create_engine(
        settings.DATABASE_URL,
        poolclass=NullPool,
        echo=settings.DEBUG,
        connect_args={"connect_timeout": 2}  # Quick timeout for optional DB
    )
else:
    # Create a dummy engine that won't actually connect
    engine = None

# Create SessionLocal class for database sessions (only if engine exists)
if engine is not None:
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
else:
    SessionLocal = None

# Base class for declarative models
Base = declarative_base()

def init_db():
    """
    Initialize database: create tables and enable PostGIS extension
    Database is OPTIONAL - app works perfectly without it
    """
    # Skip if database is not enabled
    if not settings.USE_DATABASE or engine is None:
        return  # Database disabled, skip silently
    
    try:
        # Quick connection test with timeout
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))  # Simple connection test
        
        # If connection works, proceed with initialization
        Base.metadata.create_all(bind=engine)
        
        # Enable PostGIS extension
        try:
            with engine.connect() as conn:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
                conn.commit()
            print("✅ Database connected and initialized successfully")
        except Exception:
            pass
        
    except Exception:
        # Database not available or not configured - this is OK!
        # Silently skip database initialization
        pass  # Database is optional, no need to print warnings

def get_db():
    """
    Dependency function for FastAPI to get database session
    
    Usage:
        @app.get("/endpoint")
        def endpoint(db: Session = Depends(get_db)):
            ...
    """
    if SessionLocal is None:
        # Database not available, return None
        return None
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

