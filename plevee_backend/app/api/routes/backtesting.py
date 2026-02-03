"""
Backtesting routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from decimal import Decimal
from uuid import UUID
from datetime import datetime, date

from app.core.database.session import get_db
from app.core.database.models import User, BacktestResult, Strategy
from app.core.auth.security import get_current_user

router = APIRouter()


class RunBacktestRequest(BaseModel):
    strategy_id: UUID
    start_date: date
    end_date: date
    initial_capital: Decimal = Decimal("10000")
    parameters: Optional[Dict[str, Any]] = None


class BacktestResultResponse(BaseModel):
    id: UUID
    strategy_id: UUID
    start_date: date
    end_date: date
    initial_capital: Decimal
    final_capital: Decimal
    total_return: Decimal
    total_trades: int
    winning_trades: int
    losing_trades: int
    max_drawdown: Decimal
    sharpe_ratio: Optional[Decimal]
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.post("/run", response_model=BacktestResultResponse, status_code=status.HTTP_201_CREATED)
async def run_backtest(
    request: RunBacktestRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Run a backtest for a strategy"""
    # Verify strategy belongs to user
    strategy = db.query(Strategy).filter(
        Strategy.id == request.strategy_id,
        Strategy.user_id == current_user.id
    ).first()
    
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found"
        )
    
    # Simulate backtest results (in production, this would run actual backtest)
    # For now, generate sample results
    final_capital = request.initial_capital * Decimal("1.15")  # 15% return
    total_return = ((final_capital - request.initial_capital) / request.initial_capital) * 100
    
    backtest = BacktestResult(
        strategy_id=request.strategy_id,
        start_date=request.start_date,
        end_date=request.end_date,
        initial_capital=request.initial_capital,
        final_capital=final_capital,
        total_return=total_return,
        total_trades=25,
        winning_trades=17,
        losing_trades=8,
        max_drawdown=Decimal("-8.5"),
        sharpe_ratio=Decimal("1.8")
    )
    
    db.add(backtest)
    db.commit()
    db.refresh(backtest)
    
    return backtest


@router.get("/results", response_model=List[BacktestResultResponse])
async def get_backtest_results(
    strategy_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get backtest results for user's strategies"""
    query = db.query(BacktestResult).join(BacktestResult.strategy).filter(
        BacktestResult.strategy.has(user_id=current_user.id)
    )
    
    if strategy_id:
        query = query.filter(BacktestResult.strategy_id == strategy_id)
    
    results = query.order_by(BacktestResult.created_at.desc()).limit(50).all()
    return results


@router.get("/results/{backtest_id}", response_model=BacktestResultResponse)
async def get_backtest_result(
    backtest_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific backtest result"""
    backtest = db.query(BacktestResult).join(BacktestResult.strategy).filter(
        BacktestResult.id == backtest_id,
        BacktestResult.strategy.has(user_id=current_user.id)
    ).first()
    
    if not backtest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Backtest result not found"
        )
    
    return backtest
