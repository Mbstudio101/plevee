"""
Trading routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal
from uuid import UUID
from datetime import datetime

from app.core.database.session import get_db
from app.core.database.models import User, Trade, Position
from app.core.auth.security import get_current_user

router = APIRouter()


class CreateTradeRequest(BaseModel):
    portfolio_id: UUID
    symbol: str
    side: str  # 'buy' or 'sell'
    quantity: Decimal
    price: Decimal
    order_type: str = "market"  # 'market' or 'limit'


class TradeResponse(BaseModel):
    id: UUID
    portfolio_id: UUID
    symbol: str
    side: str
    quantity: Decimal
    price: Decimal
    total_value: Decimal
    order_type: str
    status: str
    executed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class PositionResponse(BaseModel):
    id: UUID
    portfolio_id: UUID
    symbol: str
    quantity: Decimal
    average_price: Decimal
    current_price: Decimal
    unrealized_pnl: Decimal
    
    class Config:
        from_attributes = True


@router.get("/history", response_model=List[TradeResponse])
async def get_trade_history(
    portfolio_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get trade history for user's portfolios"""
    query = db.query(Trade).join(Trade.portfolio).filter(
        Trade.portfolio.has(user_id=current_user.id)
    )
    
    if portfolio_id:
        query = query.filter(Trade.portfolio_id == portfolio_id)
    
    trades = query.order_by(Trade.executed_at.desc()).limit(100).all()
    return trades


@router.get("/positions", response_model=List[PositionResponse])
async def get_positions(
    portfolio_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current positions for user's portfolios"""
    query = db.query(Position).join(Position.portfolio).filter(
        Position.portfolio.has(user_id=current_user.id),
        Position.quantity > 0
    )
    
    if portfolio_id:
        query = query.filter(Position.portfolio_id == portfolio_id)
    
    positions = query.all()
    return positions


@router.post("/execute", response_model=TradeResponse, status_code=status.HTTP_201_CREATED)
async def execute_trade(
    request: CreateTradeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Execute a trade (paper trading for now)"""
    # Verify portfolio belongs to user
    from app.core.database.models import Portfolio
    portfolio = db.query(Portfolio).filter(
        Portfolio.id == request.portfolio_id,
        Portfolio.user_id == current_user.id
    ).first()
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    
    # Calculate total value
    total_value = request.quantity * request.price
    
    # Create trade record
    trade = Trade(
        portfolio_id=request.portfolio_id,
        symbol=request.symbol,
        side=request.side,
        quantity=request.quantity,
        price=request.price,
        total_value=total_value,
        order_type=request.order_type,
        status="executed",
        executed_at=datetime.utcnow()
    )
    
    db.add(trade)
    db.commit()
    db.refresh(trade)
    
    return trade
