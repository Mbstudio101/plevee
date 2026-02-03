"""
Trading strategy routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any
from uuid import UUID

from app.core.database.session import get_db
from app.core.database.models import User, Strategy, Portfolio
from app.core.auth.security import get_current_user

router = APIRouter()


class CreateStrategyRequest(BaseModel):
    portfolio_id: UUID
    name: str
    description: str = ""
    strategy_type: str  # golden_cross, rsi, macd, custom
    asset_class: str  # crypto, stocks, forex, commodities
    symbols: List[str]
    parameters: Dict[str, Any]


class StrategyResponse(BaseModel):
    id: UUID
    portfolio_id: UUID
    name: str
    description: str
    strategy_type: str
    asset_class: str
    symbols: List[str]
    parameters: Dict[str, Any]
    is_active: bool
    
    class Config:
        from_attributes = True


@router.post("/", response_model=StrategyResponse, status_code=status.HTTP_201_CREATED)
async def create_strategy(
    request: CreateStrategyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new trading strategy"""
    # Verify portfolio exists and belongs to user
    portfolio = db.query(Portfolio).filter(
        Portfolio.id == request.portfolio_id,
        Portfolio.user_id == current_user.id
    ).first()
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    
    # Create strategy
    strategy = Strategy(
        user_id=current_user.id,
        portfolio_id=request.portfolio_id,
        name=request.name,
        description=request.description,
        strategy_type=request.strategy_type,
        asset_class=request.asset_class,
        symbols=request.symbols,
        parameters=request.parameters,
        is_active=False
    )
    
    db.add(strategy)
    db.commit()
    db.refresh(strategy)
    
    return strategy


@router.get("/", response_model=List[StrategyResponse])
async def get_strategies(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all strategies for current user"""
    strategies = db.query(Strategy).filter(Strategy.user_id == current_user.id).all()
    return strategies


@router.patch("/{strategy_id}/activate")
async def activate_strategy(
    strategy_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Activate a trading strategy"""
    strategy = db.query(Strategy).filter(
        Strategy.id == strategy_id,
        Strategy.user_id == current_user.id
    ).first()
    
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found"
        )
    
    strategy.is_active = True
    db.commit()
    
    # Spawn Celery worker task for strategy execution
    from app.tasks.strategy_executor import execute_strategy
    task = execute_strategy.delay(str(strategy_id))
    
    print(f"Strategy {strategy.id} activated. Celery task ID: {task.id}")
    
    return {
        "message": "Strategy activated successfully",
        "strategy_id": str(strategy_id),
        "task_id": task.id
    }


@router.patch("/{strategy_id}/deactivate")
async def deactivate_strategy(
    strategy_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deactivate a trading strategy"""
    strategy = db.query(Strategy).filter(
        Strategy.id == strategy_id,
        Strategy.user_id == current_user.id
    ).first()
    
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found"
        )
    
    strategy.is_active = False
    db.commit()
    
    return {"message": "Strategy deactivated successfully", "strategy_id": str(strategy_id)}
