"""
Polymarket prediction market routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from decimal import Decimal
from uuid import UUID

from app.core.database.session import get_db
from app.core.database.models import User
from app.core.auth.security import get_current_user
from app.core.services.polymarket import get_polymarket_service
from app.config import settings

router = APIRouter()


class MarketResponse(BaseModel):
    condition_id: str
    question: str
    description: str
    end_date: str
    outcomes: List[str]
    volume: str
    liquidity: str


class PlaceOrderRequest(BaseModel):
    token_id: str
    side: str  # "BUY" or "SELL"
    price: Decimal  # 0-1 range
    size: Decimal  # Number of shares


class OrderResponse(BaseModel):
    order_id: Optional[str]
    status: str
    message: str


@router.get("/markets", response_model=List[Dict[str, Any]])
async def get_markets(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user)
):
    """
    Get available prediction markets
    
    Returns list of active prediction markets with details
    """
    polymarket = get_polymarket_service(
        api_key=settings.POLYMARKET_API_KEY,
        api_secret=settings.POLYMARKET_API_SECRET,
        api_passphrase=settings.POLYMARKET_API_PASSPHRASE
    )
    
    markets = polymarket.get_markets(limit=limit, offset=offset)
    return markets


@router.get("/markets/{condition_id}")
async def get_market(
    condition_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get details for a specific prediction market"""
    polymarket = get_polymarket_service(
        api_key=settings.POLYMARKET_API_KEY,
        api_secret=settings.POLYMARKET_API_SECRET,
        api_passphrase=settings.POLYMARKET_API_PASSPHRASE
    )
    
    market = polymarket.get_market_by_id(condition_id)
    
    if not market:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Market not found"
        )
    
    return market


@router.get("/search")
async def search_markets(
    query: str,
    limit: int = 10,
    current_user: User = Depends(get_current_user)
):
    """
    Search prediction markets by keyword
    
    Example: /api/v1/polymarket/search?query=bitcoin&limit=5
    """
    polymarket = get_polymarket_service(
        api_key=settings.POLYMARKET_API_KEY,
        api_secret=settings.POLYMARKET_API_SECRET,
        api_passphrase=settings.POLYMARKET_API_PASSPHRASE
    )
    
    results = polymarket.search_markets(query, limit)
    return results


@router.get("/events")
async def get_events(
    limit: int = 20,
    current_user: User = Depends(get_current_user)
):
    """
    Get events (groups of related markets)
    
    Events group multiple markets together, like "2024 Presidential Election"
    """
    polymarket = get_polymarket_service(
        api_key=settings.POLYMARKET_API_KEY,
        api_secret=settings.POLYMARKET_API_SECRET,
        api_passphrase=settings.POLYMARKET_API_PASSPHRASE
    )
    
    events = polymarket.get_events(limit)
    return events


@router.get("/price/{token_id}")
async def get_price(
    token_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get current mid-market price for a token"""
    polymarket = get_polymarket_service(
        api_key=settings.POLYMARKET_API_KEY,
        api_secret=settings.POLYMARKET_API_SECRET,
        api_passphrase=settings.POLYMARKET_API_PASSPHRASE
    )
    
    price = polymarket.get_price(token_id)
    
    if price is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Price not available"
        )
    
    return {"token_id": token_id, "price": float(price)}


@router.get("/orderbook/{token_id}")
async def get_orderbook(
    token_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get order book for a market token"""
    polymarket = get_polymarket_service(
        api_key=settings.POLYMARKET_API_KEY,
        api_secret=settings.POLYMARKET_API_SECRET,
        api_passphrase=settings.POLYMARKET_API_PASSPHRASE
    )
    
    orderbook = polymarket.get_orderbook(token_id)
    return orderbook


@router.post("/orders", response_model=OrderResponse)
async def place_order(
    request: PlaceOrderRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Place an order on a prediction market
    
    Price should be between 0 and 1 (e.g., 0.65 = 65% probability)
    """
    # Validate price range
    if request.price < 0 or request.price > 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Price must be between 0 and 1"
        )
    
    # Validate side
    if request.side not in ["BUY", "SELL"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Side must be 'BUY' or 'SELL'"
        )
    
    polymarket = get_polymarket_service(
        api_key=settings.POLYMARKET_API_KEY,
        api_secret=settings.POLYMARKET_API_SECRET,
        api_passphrase=settings.POLYMARKET_API_PASSPHRASE
    )
    
    order = polymarket.place_order(
        token_id=request.token_id,
        side=request.side,
        price=request.price,
        size=request.size
    )
    
    if not order:
        return OrderResponse(
            order_id=None,
            status="error",
            message="Failed to place order. Check API credentials."
        )
    
    return OrderResponse(
        order_id=order.get("order_id"),
        status="success",
        message="Order placed successfully"
    )


@router.delete("/orders/{order_id}")
async def cancel_order(
    order_id: str,
    current_user: User = Depends(get_current_user)
):
    """Cancel an existing order"""
    polymarket = get_polymarket_service(
        api_key=settings.POLYMARKET_API_KEY,
        api_secret=settings.POLYMARKET_API_SECRET,
        api_passphrase=settings.POLYMARKET_API_PASSPHRASE
    )
    
    success = polymarket.cancel_order(order_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to cancel order"
        )
    
    return {"message": "Order cancelled successfully"}


@router.get("/positions")
async def get_positions(
    current_user: User = Depends(get_current_user)
):
    """Get current prediction market positions"""
    polymarket = get_polymarket_service(
        api_key=settings.POLYMARKET_API_KEY,
        api_secret=settings.POLYMARKET_API_SECRET,
        api_passphrase=settings.POLYMARKET_API_PASSPHRASE
    )
    
    positions = polymarket.get_positions()
    return positions


@router.get("/balance")
async def get_balance(
    current_user: User = Depends(get_current_user)
):
    """Get Polymarket account balance"""
    polymarket = get_polymarket_service(
        api_key=settings.POLYMARKET_API_KEY,
        api_secret=settings.POLYMARKET_API_SECRET,
        api_passphrase=settings.POLYMARKET_API_PASSPHRASE
    )
    
    balance = polymarket.get_balance()
    return balance
