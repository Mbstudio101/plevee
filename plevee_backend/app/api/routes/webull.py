"""
Webull stock trading routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from decimal import Decimal

from app.core.database.models import User
from app.core.auth.security import get_current_user
from app.core.services.webull import get_webull_service
from app.config import settings

router = APIRouter()


class PlaceOrderRequest(BaseModel):
    symbol: str
    side: str  # "BUY" or "SELL"
    quantity: int
    order_type: str = "MARKET"  # MARKET, LIMIT, STOP, STOP_LIMIT
    price: Optional[Decimal] = None
    time_in_force: str = "DAY"  # DAY, GTC, IOC, FOK


@router.get("/quote/{symbol}")
async def get_quote(
    symbol: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get real-time quote for a stock
    
    Example: /api/v1/webull/quote/AAPL
    """
    webull = get_webull_service(
        app_key=settings.WEBULL_APP_KEY,
        app_secret=settings.WEBULL_APP_SECRET
    )
    
    quote = webull.get_quote(symbol.upper())
    
    if not quote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quote not found for {symbol}"
        )
    
    return quote


@router.get("/bars/{symbol}")
async def get_bars(
    symbol: str,
    timeframe: str = "1D",
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    """
    Get historical price bars
    
    Timeframes: 1m, 5m, 15m, 1h, 1D, 1W, 1M
    """
    webull = get_webull_service(
        app_key=settings.WEBULL_APP_KEY,
        app_secret=settings.WEBULL_APP_SECRET
    )
    
    bars = webull.get_bars(symbol.upper(), timeframe, limit)
    return bars


@router.get("/search")
async def search_symbols(
    query: str,
    current_user: User = Depends(get_current_user)
):
    """
    Search for stock symbols
    
    Example: /api/v1/webull/search?query=apple
    """
    webull = get_webull_service(
        app_key=settings.WEBULL_APP_KEY,
        app_secret=settings.WEBULL_APP_SECRET
    )
    
    results = webull.search_symbols(query)
    return results


@router.post("/orders")
async def place_order(
    request: PlaceOrderRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Place a stock order
    
    Order types: MARKET, LIMIT, STOP, STOP_LIMIT
    Time in force: DAY, GTC, IOC, FOK
    """
    # Validate order type
    if request.order_type not in ["MARKET", "LIMIT", "STOP", "STOP_LIMIT"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid order type"
        )
    
    # Validate price for LIMIT orders
    if request.order_type in ["LIMIT", "STOP_LIMIT"] and not request.price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Price required for LIMIT orders"
        )
    
    webull = get_webull_service(
        app_key=settings.WEBULL_APP_KEY,
        app_secret=settings.WEBULL_APP_SECRET
    )
    
    order = webull.place_order(
        symbol=request.symbol.upper(),
        side=request.side,
        quantity=request.quantity,
        order_type=request.order_type,
        price=request.price,
        time_in_force=request.time_in_force
    )
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to place order. Check API credentials."
        )
    
    return order


@router.delete("/orders/{order_id}")
async def cancel_order(
    order_id: str,
    current_user: User = Depends(get_current_user)
):
    """Cancel an order"""
    webull = get_webull_service(
        app_key=settings.WEBULL_APP_KEY,
        app_secret=settings.WEBULL_APP_SECRET
    )
    
    success = webull.cancel_order(order_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to cancel order"
        )
    
    return {"message": "Order cancelled successfully"}


@router.get("/account")
async def get_account(
    current_user: User = Depends(get_current_user)
):
    """Get account information"""
    webull = get_webull_service(
        app_key=settings.WEBULL_APP_KEY,
        app_secret=settings.WEBULL_APP_SECRET
    )
    
    account = webull.get_account()
    return account


@router.get("/positions")
async def get_positions(
    current_user: User = Depends(get_current_user)
):
    """Get current stock positions"""
    webull = get_webull_service(
        app_key=settings.WEBULL_APP_KEY,
        app_secret=settings.WEBULL_APP_SECRET
    )
    
    positions = webull.get_positions()
    return positions


@router.get("/orders")
async def get_orders(
    status_filter: str = "all",
    current_user: User = Depends(get_current_user)
):
    """
    Get order history
    
    Status: all, open, closed
    """
    webull = get_webull_service(
        app_key=settings.WEBULL_APP_KEY,
        app_secret=settings.WEBULL_APP_SECRET
    )
    
    orders = webull.get_orders(status=status_filter)
    return orders
