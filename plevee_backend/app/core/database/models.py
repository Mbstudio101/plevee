"""
Database models for Plevee Trading Platform
"""
from sqlalchemy import Column, String, Boolean, DECIMAL, TIMESTAMP, ForeignKey, Text, Integer, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.core.database.session import Base


class User(Base):
    """User account model"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String(255))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    portfolios = relationship("Portfolio", back_populates="user", cascade="all, delete-orphan")
    strategies = relationship("Strategy", back_populates="user", cascade="all, delete-orphan")
    exchange_connections = relationship("ExchangeConnection", back_populates="user", cascade="all, delete-orphan")


class Portfolio(Base):
    """Portfolio model"""
    __tablename__ = "portfolios"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    initial_balance = Column(DECIMAL(20, 8), nullable=False)
    current_balance = Column(DECIMAL(20, 8), nullable=False)
    currency = Column(String(10), default="USD")
    is_paper_trading = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="portfolios")
    strategies = relationship("Strategy", back_populates="portfolio", cascade="all, delete-orphan")
    trades = relationship("Trade", back_populates="portfolio", cascade="all, delete-orphan")
    positions = relationship("Position", back_populates="portfolio", cascade="all, delete-orphan")


class ExchangeConnection(Base):
    """Exchange API connection model"""
    __tablename__ = "exchange_connections"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    exchange_name = Column(String(100), nullable=False)
    asset_class = Column(String(50), nullable=False)  # crypto, stocks, forex, commodities
    api_key_encrypted = Column(Text, nullable=False)
    api_secret_encrypted = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    is_paper_trading = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="exchange_connections")


class Strategy(Base):
    """Trading strategy model"""
    __tablename__ = "strategies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    portfolio_id = Column(UUID(as_uuid=True), ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    strategy_type = Column(String(100), nullable=False)  # golden_cross, rsi, macd, custom
    asset_class = Column(String(50), nullable=False)
    symbols = Column(ARRAY(Text))  # Array of trading symbols
    parameters = Column(JSONB, nullable=False)  # Strategy-specific parameters
    is_active = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="strategies")
    portfolio = relationship("Portfolio", back_populates="strategies")
    trades = relationship("Trade", back_populates="strategy")
    backtest_results = relationship("BacktestResult", back_populates="strategy", cascade="all, delete-orphan")


class Trade(Base):
    """Trade execution model"""
    __tablename__ = "trades"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    portfolio_id = Column(UUID(as_uuid=True), ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False)
    strategy_id = Column(UUID(as_uuid=True), ForeignKey("strategies.id", ondelete="SET NULL"))
    exchange_name = Column(String(100), nullable=False)
    symbol = Column(String(50), nullable=False)
    asset_class = Column(String(50), nullable=False)
    side = Column(String(10), nullable=False)  # buy, sell
    order_type = Column(String(20), nullable=False)  # market, limit, stop
    quantity = Column(DECIMAL(20, 8), nullable=False)
    price = Column(DECIMAL(20, 8))
    executed_price = Column(DECIMAL(20, 8))
    status = Column(String(50), nullable=False)  # pending, filled, partial, cancelled, failed
    order_id = Column(String(255))  # Exchange order ID
    fees = Column(DECIMAL(20, 8))
    profit_loss = Column(DECIMAL(20, 8))
    executed_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="trades")
    strategy = relationship("Strategy", back_populates="trades")


class Position(Base):
    """Current position model"""
    __tablename__ = "positions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    portfolio_id = Column(UUID(as_uuid=True), ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False)
    symbol = Column(String(50), nullable=False)
    asset_class = Column(String(50), nullable=False)
    quantity = Column(DECIMAL(20, 8), nullable=False)
    average_entry_price = Column(DECIMAL(20, 8), nullable=False)
    current_price = Column(DECIMAL(20, 8))
    unrealized_pnl = Column(DECIMAL(20, 8))
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="positions")


class BacktestResult(Base):
    """Backtest results model"""
    __tablename__ = "backtest_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    strategy_id = Column(UUID(as_uuid=True), ForeignKey("strategies.id", ondelete="CASCADE"), nullable=False)
    start_date = Column(TIMESTAMP, nullable=False)
    end_date = Column(TIMESTAMP, nullable=False)
    initial_capital = Column(DECIMAL(20, 8), nullable=False)
    final_capital = Column(DECIMAL(20, 8), nullable=False)
    total_return = Column(DECIMAL(10, 4))
    sharpe_ratio = Column(DECIMAL(10, 4))
    max_drawdown = Column(DECIMAL(10, 4))
    win_rate = Column(DECIMAL(10, 4))
    total_trades = Column(Integer)
    winning_trades = Column(Integer)
    losing_trades = Column(Integer)
    metrics = Column(JSONB)  # Additional metrics
    equity_curve = Column(JSONB)  # Time series data
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    strategy = relationship("Strategy", back_populates="backtest_results")


class MarketData(Base):
    """Market data time series (TimescaleDB hypertable)"""
    __tablename__ = "market_data"
    
    time = Column(TIMESTAMP, primary_key=True, nullable=False)
    symbol = Column(String(50), primary_key=True, nullable=False)
    asset_class = Column(String(50), nullable=False)
    exchange = Column(String(100))
    open = Column(DECIMAL(20, 8))
    high = Column(DECIMAL(20, 8))
    low = Column(DECIMAL(20, 8))
    close = Column(DECIMAL(20, 8))
    volume = Column(DECIMAL(20, 8))
    interval = Column(String(10))  # 1m, 5m, 15m, 1h, 1d
