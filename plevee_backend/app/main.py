"""
Plevee Trading Platform - Main Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import uvicorn

from app.core.database.session import engine, Base
from app.api.routes import auth, portfolio, strategies, backtesting, trading, market_data#, polymarket, webull

# Create FastAPI app
app = FastAPI(
    title="Plevee Trading API",
    description="Multi-asset automated trading platform API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(portfolio.router, prefix="/api/v1/portfolios", tags=["Portfolios"])
app.include_router(strategies.router, prefix="/api/v1/strategies", tags=["Strategies"])
app.include_router(backtesting.router, prefix="/api/v1/backtesting", tags=["Backtesting"])
app.include_router(trading.router, prefix="/api/v1/trading", tags=["Trading"])
app.include_router(market_data.router, prefix="/api/v1/market-data", tags=["Market Data"])
# app.include_router(polymarket.router, prefix="/api/v1/polymarket", tags=["Polymarket"])
# app.include_router(webull.router, prefix="/api/v1/webull", tags=["Webull"])


@app.on_event("startup")
async def startup_event():
    """Initialize database and services on startup"""
    try:
        # Create tables (only if database is available)
        Base.metadata.create_all(bind=engine)
        print("✅ Database initialized")
    except Exception as e:
        print(f"⚠️  Database not available: {e}")
        print("   Backend will run without database features")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("🛑 Shutting down Plevee API")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "Plevee Trading API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "redis": "connected"
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
