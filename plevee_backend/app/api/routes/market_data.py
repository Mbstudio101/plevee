"""
Market data routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal
from datetime import datetime, date
from uuid import UUID

from app.core.database.session import get_db
from app.core.database.models import User, MarketData
from app.core.auth.security import get_current_user

router = APIRouter()


class PriceQuote(BaseModel):
    symbol: str
    price: Decimal
    change: Decimal
    change_percent: Decimal
    volume: int
    timestamp: datetime


class HistoricalDataPoint(BaseModel):
    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int


class MarketDataResponse(BaseModel):
    id: UUID
    symbol: str
    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int
    
    class Config:
        from_attributes = True


@router.get("/quote/{symbol}", response_model=PriceQuote)
async def get_quote(
    symbol: str,
    current_user: User = Depends(get_current_user)
):
    """Get real-time quote for a symbol (simulated for now)"""
    # In production, this would fetch from real market data provider
    # For now, return simulated data
    import random
    
    base_price = Decimal("100.00")
    change = Decimal(str(random.uniform(-5, 5)))
    current_price = base_price + change
    change_percent = (change / base_price) * 100
    
    return PriceQuote(
        symbol=symbol.upper(),
        price=current_price,
        change=change,
        change_percent=change_percent,
        volume=random.randint(1000000, 10000000),
        timestamp=datetime.utcnow()
    )


@router.get("/historical/{symbol}", response_model=List[MarketDataResponse])
async def get_historical_data(
    symbol: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    interval: str = "1d",  # 1m, 5m, 15m, 1h, 1d
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get historical market data for a symbol"""
    query = db.query(MarketData).filter(MarketData.symbol == symbol.upper())
    
    if start_date:
        query = query.filter(MarketData.timestamp >= start_date)
    if end_date:
        query = query.filter(MarketData.timestamp <= end_date)
    
    data = query.order_by(MarketData.timestamp.desc()).limit(1000).all()
    
    # If no data in database, return empty list
    # In production, this would fetch from market data provider
    return data


@router.get("/search")
async def search_symbols(
    query: str,
    limit: int = 10,
    current_user: User = Depends(get_current_user)
):
    """Search for symbols (simulated for now)"""
    # In production, this would search real symbol database
    # For now, return sample symbols
    symbols = [
        {"symbol": "AAPL", "name": "Apple Inc.", "type": "stock"},
        {"symbol": "GOOGL", "name": "Alphabet Inc.", "type": "stock"},
        {"symbol": "MSFT", "name": "Microsoft Corporation", "type": "stock"},
        {"symbol": "BTC-USD", "name": "Bitcoin USD", "type": "crypto"},
        {"symbol": "ETH-USD", "name": "Ethereum USD", "type": "crypto"},
    ]
    
    # Filter by query
    filtered = [s for s in symbols if query.upper() in s["symbol"] or query.upper() in s["name"].upper()]
    return filtered[:limit]


@router.get("/watchlist")
async def get_watchlist(
    current_user: User = Depends(get_current_user)
):
    """Get user's watchlist (placeholder for now)"""
    # In production, this would fetch from user's saved watchlist
    return {
        "symbols": ["AAPL", "GOOGL", "BTC-USD", "ETH-USD"],
        "message": "Watchlist management coming soon"
    }
