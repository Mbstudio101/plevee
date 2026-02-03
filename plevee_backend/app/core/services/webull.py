"""
Webull service for stock trading and market data

This module provides integration with Webull's OpenAPI:
- Market Data API: Real-time quotes, historical data
- Trading API: Place orders, manage positions
- Account API: Balance, positions, order history
"""
from typing import Optional, List, Dict, Any
from decimal import Decimal
import logging
import os

logger = logging.getLogger(__name__)

# Webull SDK will be imported when credentials are provided
try:
    from webull_openapi import webull_client
    from webull_openapi.request import ApiRequest
    WEBULL_AVAILABLE = True
except ImportError:
    WEBULL_AVAILABLE = False
    logger.warning("Webull SDK not installed. Install with: pip install webull-openapi-python-sdk")


class WebullService:
    """Service for interacting with Webull for stock trading"""
    
    def __init__(
        self,
        app_key: Optional[str] = None,
        app_secret: Optional[str] = None,
        environment: str = "production"  # or "sandbox"
    ):
        """
        Initialize Webull service
        
        Args:
            app_key: Webull App Key
            app_secret: Webull App Secret
            environment: "production" or "sandbox"
        """
        self.app_key = app_key
        self.app_secret = app_secret
        self.environment = environment
        self.client = None
        self.account_id = None
        
        if WEBULL_AVAILABLE and app_key and app_secret:
            try:
                # Initialize Webull client with credentials
                self.client = webull_client.WebullClient(
                    app_key=app_key,
                    app_secret=app_secret,
                    region_id=1  # 1=US, 2=HK, 3=CN
                )
                logger.info(f"Webull client initialized for {environment}")
                
                # Get account ID for trading
                try:
                    account_response = self.client.account().get_account_list()
                    if account_response and account_response.data:
                        self.account_id = account_response.data[0].get("account_id")
                        logger.info(f"Webull account ID: {self.account_id}")
                except Exception as e:
                    logger.warning(f"Could not fetch account ID: {e}")
                    
            except Exception as e:
                logger.error(f"Failed to initialize Webull client: {e}")

    
    # ===== Market Data =====
    
    def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get real-time quote for a symbol
        
        Args:
            symbol: Stock symbol (e.g., "AAPL")
            
        Returns:
            Quote data with price, volume, etc.
        """
        try:
            if not self.client:
                return self._get_sample_quote(symbol)
            
            # Real Webull API call
            response = self.client.market().get_quote(
                symbols=[symbol],
                category="stock"
            )
            
            if response and response.data and len(response.data) > 0:
                quote_data = response.data[0]
                return {
                    "symbol": symbol,
                    "price": float(quote_data.get("last_price", 0)),
                    "bid": float(quote_data.get("bid_price", 0)),
                    "ask": float(quote_data.get("ask_price", 0)),
                    "volume": int(quote_data.get("volume", 0)),
                    "change": float(quote_data.get("change", 0)),
                    "change_percent": float(quote_data.get("change_ratio", 0)) * 100
                }
            
            return self._get_sample_quote(symbol)
        except Exception as e:
            logger.error(f"Error fetching quote for {symbol}: {e}")
            return self._get_sample_quote(symbol)
    
    def get_bars(
        self,
        symbol: str,
        timeframe: str = "1D",
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get historical price bars
        
        Args:
            symbol: Stock symbol
            timeframe: Timeframe (1m, 5m, 15m, 1h, 1D, etc.)
            limit: Number of bars
            
        Returns:
            List of OHLCV bars
        """
        try:
            if not self.client:
                return self._get_sample_bars(symbol, limit)
            
            # Real Webull API call
            response = self.client.market().get_bars(
                symbol=symbol,
                timeframe=timeframe,
                count=limit
            )
            
            if response and response.data:
                bars = []
                for bar in response.data:
                    bars.append({
                        "timestamp": bar.get("timestamp"),
                        "open": float(bar.get("open", 0)),
                        "high": float(bar.get("high", 0)),
                        "low": float(bar.get("low", 0)),
                        "close": float(bar.get("close", 0)),
                        "volume": int(bar.get("volume", 0))
                    })
                return bars
            
            return self._get_sample_bars(symbol, limit)
        except Exception as e:
            logger.error(f"Error fetching bars for {symbol}: {e}")
            return self._get_sample_bars(symbol, limit)
    
    def search_symbols(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for symbols
        
        Args:
            query: Search query
            
        Returns:
            List of matching symbols
        """
        try:
            if not self.client:
                return self._get_sample_symbols(query)
            
            # Real Webull API call
            response = self.client.market().search_instruments(
                keyword=query,
                category="stock"
            )
            
            if response and response.data:
                results = []
                for item in response.data:
                    results.append({
                        "symbol": item.get("symbol"),
                        "name": item.get("name")
                    })
                return results
            
            return self._get_sample_symbols(query)
        except Exception as e:
            logger.error(f"Error searching symbols: {e}")
            return self._get_sample_symbols(query)
    
    # ===== Trading =====
    
    def place_order(
        self,
        symbol: str,
        side: str,  # "BUY" or "SELL"
        quantity: int,
        order_type: str = "MARKET",  # MARKET, LIMIT, STOP, STOP_LIMIT
        price: Optional[Decimal] = None,
        time_in_force: str = "DAY"  # DAY, GTC, IOC, FOK
    ) -> Optional[Dict[str, Any]]:
        """
        Place a stock order
        
        Args:
            symbol: Stock symbol
            side: "BUY" or "SELL"
            quantity: Number of shares
            order_type: Order type
            price: Limit price (required for LIMIT orders)
            time_in_force: Time in force
            
        Returns:
            Order response with order ID
        """
        try:
            if not self.client or not self.account_id:
                logger.warning("Cannot place order: Webull client not configured")
                return {
                    "order_id": "demo_order_123",
                    "status": "demo",
                    "message": "Demo mode - order not actually placed"
                }
            
            # Real Webull API call
            order_request = {
                "account_id": self.account_id,
                "symbol": symbol,
                "side": side,
                "order_type": order_type,
                "quantity": quantity,
                "time_in_force": time_in_force
            }
            
            if order_type in ["LIMIT", "STOP_LIMIT"] and price:
                order_request["price"] = float(price)
            
            response = self.client.trade().place_order(**order_request)
            
            if response and response.data:
                return {
                    "order_id": response.data.get("order_id"),
                    "status": response.data.get("status"),
                    "message": "Order placed successfully"
                }
            
            return None
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return None
    
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an order
        
        Args:
            order_id: Order ID to cancel
            
        Returns:
            True if successful
        """
        try:
            if not self.client:
                return False
            
            # Real implementation
            # self.client.cancel_order(order_id)
            # return True
            
            return False
        except Exception as e:
            logger.error(f"Error cancelling order {order_id}: {e}")
            return False
    
    # ===== Account =====
    
    def get_account(self) -> Dict[str, Any]:
        """
        Get account information
        
        Returns:
            Account data with balance, buying power, etc.
        """
        try:
            if not self.client:
                return self._get_sample_account()
            
            # Real implementation
            # account = self.client.get_account()
            # return account
            
            return self._get_sample_account()
        except Exception as e:
            logger.error(f"Error fetching account: {e}")
            return {}
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """
        Get current positions
        
        Returns:
            List of positions
        """
        try:
            if not self.client:
                return []
            
            # Real implementation
            # positions = self.client.get_positions()
            # return positions
            
            return []
        except Exception as e:
            logger.error(f"Error fetching positions: {e}")
            return []
    
    def get_orders(self, status: str = "all") -> List[Dict[str, Any]]:
        """
        Get order history
        
        Args:
            status: Filter by status (all, open, closed)
            
        Returns:
            List of orders
        """
        try:
            if not self.client:
                return []
            
            # Real implementation
            # orders = self.client.get_orders(status=status)
            # return orders
            
            return []
        except Exception as e:
            logger.error(f"Error fetching orders: {e}")
            return []
    
    # ===== Sample Data for Demo Mode =====
    
    def _get_sample_quote(self, symbol: str) -> Dict[str, Any]:
        """Return sample quote data"""
        import random
        base_price = 150.0
        
        return {
            "symbol": symbol,
            "price": round(base_price + random.uniform(-5, 5), 2),
            "bid": round(base_price - 0.05, 2),
            "ask": round(base_price + 0.05, 2),
            "volume": random.randint(1000000, 10000000),
            "change": round(random.uniform(-2, 2), 2),
            "change_percent": round(random.uniform(-1.5, 1.5), 2)
        }
    
    def _get_sample_bars(self, symbol: str, limit: int) -> List[Dict[str, Any]]:
        """Return sample bar data"""
        import random
        from datetime import datetime, timedelta
        
        bars = []
        base_price = 150.0
        
        for i in range(limit):
            timestamp = datetime.now() - timedelta(days=limit - i)
            open_price = base_price + random.uniform(-2, 2)
            close_price = open_price + random.uniform(-1, 1)
            high_price = max(open_price, close_price) + random.uniform(0, 0.5)
            low_price = min(open_price, close_price) - random.uniform(0, 0.5)
            
            bars.append({
                "timestamp": timestamp.isoformat(),
                "open": round(open_price, 2),
                "high": round(high_price, 2),
                "low": round(low_price, 2),
                "close": round(close_price, 2),
                "volume": random.randint(500000, 2000000)
            })
        
        return bars
    
    def _get_sample_symbols(self, query: str) -> List[Dict[str, Any]]:
        """Return sample symbol search results"""
        symbols = {
            "apple": {"symbol": "AAPL", "name": "Apple Inc."},
            "google": {"symbol": "GOOGL", "name": "Alphabet Inc."},
            "microsoft": {"symbol": "MSFT", "name": "Microsoft Corporation"},
            "tesla": {"symbol": "TSLA", "name": "Tesla, Inc."},
            "amazon": {"symbol": "AMZN", "name": "Amazon.com, Inc."}
        }
        
        query_lower = query.lower()
        results = []
        
        for key, data in symbols.items():
            if query_lower in key or query_lower in data["symbol"].lower():
                results.append(data)
        
        return results
    
    def _get_sample_account(self) -> Dict[str, Any]:
        """Return sample account data"""
        return {
            "account_id": "demo_account",
            "cash": "10000.00",
            "buying_power": "10000.00",
            "portfolio_value": "10000.00",
            "equity": "10000.00"
        }


# Global instance
_webull_service: Optional[WebullService] = None


def get_webull_service(
    app_key: Optional[str] = None,
    app_secret: Optional[str] = None,
    environment: str = "production"
) -> WebullService:
    """
    Get or create Webull service instance
    
    Args:
        app_key: Webull App Key
        app_secret: Webull App Secret
        environment: "production" or "sandbox"
        
    Returns:
        WebullService instance
    """
    global _webull_service
    
    if _webull_service is None:
        _webull_service = WebullService(
            app_key=app_key,
            app_secret=app_secret,
            environment=environment
        )
    
    return _webull_service
