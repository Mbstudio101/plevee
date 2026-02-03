"""
Strategy executor Celery tasks

This module handles automated execution of trading strategies.
Strategies are executed as background tasks and can run continuously
or on a schedule.
"""
from celery import Task
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
from decimal import Decimal
import logging

from app.celery_app import celery_app
from app.core.database.session import SessionLocal
from app.core.database.models import Strategy, Trade, Portfolio, Position

logger = logging.getLogger(__name__)


class DatabaseTask(Task):
    """Base task with database session management"""
    _session = None

    @property
    def session(self) -> Session:
        if self._session is None:
            self._session = SessionLocal()
        return self._session

    def after_return(self, *args, **kwargs):
        if self._session is not None:
            self._session.close()
            self._session = None


@celery_app.task(base=DatabaseTask, bind=True, name="app.tasks.strategy_executor.execute_strategy")
def execute_strategy(self, strategy_id: str):
    """
    Execute a trading strategy
    
    Args:
        strategy_id: UUID of the strategy to execute
    
    Returns:
        dict: Execution results with trade count and status
    """
    logger.info(f"Starting strategy execution for strategy_id={strategy_id}")
    
    try:
        # Get strategy from database
        strategy = self.session.query(Strategy).filter(
            Strategy.id == UUID(strategy_id),
            Strategy.is_active == True
        ).first()
        
        if not strategy:
            logger.warning(f"Strategy {strategy_id} not found or inactive")
            return {"status": "error", "message": "Strategy not found or inactive"}
        
        # Get portfolio
        portfolio = self.session.query(Portfolio).filter(
            Portfolio.id == strategy.portfolio_id
        ).first()
        
        if not portfolio:
            logger.error(f"Portfolio not found for strategy {strategy_id}")
            return {"status": "error", "message": "Portfolio not found"}
        
        # Execute strategy logic
        # This is a simplified example - in production, this would:
        # 1. Fetch market data
        # 2. Run strategy indicators/signals
        # 3. Generate trading signals
        # 4. Execute trades based on signals
        
        trades_executed = 0
        
        # Example: Simple strategy execution
        # In production, this would use the strategy's parameters and indicators
        if strategy.strategy_type == "momentum":
            # Momentum strategy logic
            signal = _check_momentum_signal(strategy)
            if signal:
                trade = _execute_trade(self.session, portfolio, signal)
                if trade:
                    trades_executed += 1
        
        elif strategy.strategy_type == "mean_reversion":
            # Mean reversion strategy logic
            signal = _check_mean_reversion_signal(strategy)
            if signal:
                trade = _execute_trade(self.session, portfolio, signal)
                if trade:
                    trades_executed += 1
        
        # Update strategy last execution time
        strategy.last_executed_at = datetime.utcnow()
        self.session.commit()
        
        logger.info(f"Strategy {strategy_id} executed successfully. Trades: {trades_executed}")
        
        return {
            "status": "success",
            "strategy_id": strategy_id,
            "trades_executed": trades_executed,
            "executed_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error executing strategy {strategy_id}: {str(e)}", exc_info=True)
        self.session.rollback()
        return {"status": "error", "message": str(e)}


@celery_app.task(name="app.tasks.strategy_executor.stop_strategy")
def stop_strategy(strategy_id: str):
    """
    Stop a running strategy
    
    Args:
        strategy_id: UUID of the strategy to stop
    """
    logger.info(f"Stopping strategy {strategy_id}")
    
    session = SessionLocal()
    try:
        strategy = session.query(Strategy).filter(
            Strategy.id == UUID(strategy_id)
        ).first()
        
        if strategy:
            strategy.is_active = False
            session.commit()
            logger.info(f"Strategy {strategy_id} stopped successfully")
            return {"status": "success", "message": "Strategy stopped"}
        else:
            return {"status": "error", "message": "Strategy not found"}
            
    except Exception as e:
        logger.error(f"Error stopping strategy {strategy_id}: {str(e)}")
        session.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        session.close()


def _check_momentum_signal(strategy: Strategy) -> dict:
    """
    Check for momentum trading signals using RSI and MACD
    
    Returns:
        dict: Trading signal with symbol, side, quantity, price
    """
    try:
        # Try to import TA-Lib
        try:
            import talib
            import numpy as np
        except ImportError:
            logger.warning("TA-Lib not installed. Install with: brew install ta-lib && pip install TA-Lib")
            return None
        
        from app.core.services.webull import get_webull_service
        from app.config import settings
        
        # Get market data
        webull = get_webull_service(
            app_key=settings.WEBULL_APP_KEY,
            app_secret=settings.WEBULL_APP_SECRET
        )
        
        symbol = strategy.parameters.get("symbol", "AAPL")
        bars = webull.get_bars(symbol=symbol, timeframe="1D", limit=100)
        
        if not bars or len(bars) < 50:
            logger.warning(f"Insufficient data for {symbol}")
            return None
        
        # Extract close prices
        closes = np.array([float(bar["close"]) for bar in bars])
        
        # Calculate indicators
        rsi = talib.RSI(closes, timeperiod=14)
        macd, signal, hist = talib.MACD(closes, fastperiod=12, slowperiod=26, signalperiod=9)
        
        # Get latest values
        current_rsi = rsi[-1]
        current_macd = macd[-1]
        current_signal = signal[-1]
        current_price = closes[-1]
        
        # Generate signal
        if current_rsi < 30 and current_macd > current_signal:
            # Oversold + bullish MACD crossover = BUY
            logger.info(f"BUY signal for {symbol}: RSI={current_rsi:.2f}, MACD crossover")
            return {
                "symbol": symbol,
                "side": "BUY",
                "quantity": strategy.parameters.get("quantity", 10),
                "price": current_price
            }
        elif current_rsi > 70 and current_macd < current_signal:
            # Overbought + bearish MACD crossover = SELL
            logger.info(f"SELL signal for {symbol}: RSI={current_rsi:.2f}, MACD crossover")
            return {
                "symbol": symbol,
                "side": "SELL",
                "quantity": strategy.parameters.get("quantity", 10),
                "price": current_price
            }
        
        logger.debug(f"No signal for {symbol}: RSI={current_rsi:.2f}")
        return None
        
    except Exception as e:
        logger.error(f"Error checking momentum signal: {e}")
        return None


def _check_mean_reversion_signal(strategy: Strategy) -> dict:
    """
    Check for mean reversion trading signals using Bollinger Bands
    
    Returns:
        dict: Trading signal with symbol, side, quantity, price
    """
    try:
        # Try to import TA-Lib
        try:
            import talib
            import numpy as np
        except ImportError:
            logger.warning("TA-Lib not installed. Install with: brew install ta-lib && pip install TA-Lib")
            return None
        
        from app.core.services.webull import get_webull_service
        from app.config import settings
        
        # Get market data
        webull = get_webull_service(
            app_key=settings.WEBULL_APP_KEY,
            app_secret=settings.WEBULL_APP_SECRET
        )
        
        symbol = strategy.parameters.get("symbol", "AAPL")
        bars = webull.get_bars(symbol=symbol, timeframe="1D", limit=50)
        
        if not bars or len(bars) < 20:
            logger.warning(f"Insufficient data for {symbol}")
            return None
        
        # Extract close prices
        closes = np.array([float(bar["close"]) for bar in bars])
        
        # Calculate Bollinger Bands
        upper, middle, lower = talib.BBANDS(closes, timeperiod=20, nbdevup=2, nbdevdn=2)
        
        # Get latest values
        current_price = closes[-1]
        current_upper = upper[-1]
        current_lower = lower[-1]
        current_middle = middle[-1]
        
        # Generate signal
        if current_price < current_lower:
            # Price below lower band = BUY (expect reversion to mean)
            logger.info(f"BUY signal for {symbol}: Price ${current_price:.2f} < Lower Band ${current_lower:.2f}")
            return {
                "symbol": symbol,
                "side": "BUY",
                "quantity": strategy.parameters.get("quantity", 10),
                "price": current_price
            }
        elif current_price > current_upper:
            # Price above upper band = SELL (expect reversion to mean)
            logger.info(f"SELL signal for {symbol}: Price ${current_price:.2f} > Upper Band ${current_upper:.2f}")
            return {
                "symbol": symbol,
                "side": "SELL",
                "quantity": strategy.parameters.get("quantity", 10),
                "price": current_price
            }
        
        logger.debug(f"No signal for {symbol}: Price ${current_price:.2f} within bands")
        return None
        
    except Exception as e:
        logger.error(f"Error checking mean reversion signal: {e}")
        return None


def _execute_trade(session: Session, portfolio: Portfolio, signal: dict) -> Trade:
    """
    Execute a trade based on a signal
    
    Args:
        session: Database session
        portfolio: Portfolio to trade in
        signal: Trading signal with symbol, side, quantity, price
    
    Returns:
        Trade: Created trade object
    """
    try:
        total_value = signal["quantity"] * signal["price"]
        
        trade = Trade(
            portfolio_id=portfolio.id,
            symbol=signal["symbol"],
            side=signal["side"],
            quantity=signal["quantity"],
            price=signal["price"],
            total_value=total_value,
            order_type="market",
            status="executed",
            executed_at=datetime.utcnow()
        )
        
        session.add(trade)
        session.commit()
        
        logger.info(f"Trade executed: {signal['side']} {signal['quantity']} {signal['symbol']} @ {signal['price']}")
        
        return trade
        
    except Exception as e:
        logger.error(f"Error executing trade: {str(e)}")
        session.rollback()
        return None
