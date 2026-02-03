"""
Portfolio management routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from decimal import Decimal
from uuid import UUID

from app.core.database.session import get_db
from app.core.database.models import User, Portfolio
from app.core.auth.security import get_current_user

router = APIRouter()


class CreatePortfolioRequest(BaseModel):
    name: str
    description: str = ""
    initial_balance: Decimal
    currency: str = "USD"
    is_paper_trading: bool = True


class PortfolioResponse(BaseModel):
    id: UUID
    name: str
    description: str
    initial_balance: Decimal
    current_balance: Decimal
    currency: str
    is_paper_trading: bool
    
    class Config:
        from_attributes = True


@router.post("/", response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED)
async def create_portfolio(
    request: CreatePortfolioRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new portfolio"""
    portfolio = Portfolio(
        user_id=current_user.id,
        name=request.name,
        description=request.description,
        initial_balance=request.initial_balance,
        current_balance=request.initial_balance,
        currency=request.currency,
        is_paper_trading=request.is_paper_trading
    )
    
    db.add(portfolio)
    db.commit()
    db.refresh(portfolio)
    
    return portfolio


@router.get("/", response_model=List[PortfolioResponse])
async def get_portfolios(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all portfolios for current user"""
    portfolios = db.query(Portfolio).filter(Portfolio.user_id == current_user.id).all()
    return portfolios


@router.get("/{portfolio_id}", response_model=PortfolioResponse)
async def get_portfolio(
    portfolio_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific portfolio"""
    portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == current_user.id
    ).first()
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    
    return portfolio
