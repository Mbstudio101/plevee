"""
Polymarket service for prediction market trading

This module provides integration with Polymarket's APIs:
- Gamma API: Market discovery & metadata
- CLOB API: Trading & orderbooks
- Data API: Positions & history
"""
from typing import Optional, List, Dict, Any
from decimal import Decimal
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OrderType
import logging
import requests

logger = logging.getLogger(__name__)


class PolymarketService:
    """Service for interacting with Polymarket prediction markets"""
    
    # API endpoints
    GAMMA_API = "https://gamma-api.polymarket.com"
    CLOB_API = "https://clob.polymarket.com"
    DATA_API = "https://data-api.polymarket.com"
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        api_passphrase: Optional[str] = None,
        chain_id: int = 137  # Polygon mainnet
    ):
        """
        Initialize Polymarket service
        
        Args:
            api_key: Polymarket API key (for CLOB trading)
            api_secret: Polymarket API secret
            api_passphrase: Polymarket API passphrase
            chain_id: Blockchain network ID (137 for Polygon mainnet)
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_passphrase = api_passphrase
        self.chain_id = chain_id
        
        # Initialize CLOB client for trading (requires credentials)
        self.clob_client = None
        if api_key and api_secret and api_passphrase:
            try:
                self.clob_client = ClobClient(
                    host=self.CLOB_API,
                    key=api_key,
                    secret=api_secret,
                    passphrase=api_passphrase,
                    chain_id=chain_id
                )
                logger.info("Polymarket CLOB client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Polymarket CLOB client: {e}")
    
    # ===== GAMMA API: Market Discovery =====
    
    def get_markets(
        self,
        limit: int = 20,
        offset: int = 0,
        active: bool = True,
        closed: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get available prediction markets from Gamma API
        
        Args:
            limit: Number of markets to return
            offset: Pagination offset
            active: Include active markets
            closed: Include closed markets
            
        Returns:
            List of market dictionaries
        """
        try:
            params = {
                "limit": limit,
                "offset": offset,
                "active": active,
                "closed": closed
            }
            
            response = requests.get(
                f"{self.GAMMA_API}/markets",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            markets = response.json()
            logger.info(f"Fetched {len(markets)} markets from Gamma API")
            return markets
            
        except Exception as e:
            logger.error(f"Error fetching markets from Gamma API: {e}")
            # Return sample markets as fallback
            return self._get_sample_markets()
    
    def get_market_by_id(self, condition_id: str) -> Optional[Dict[str, Any]]:
        """
        Get details for a specific market from Gamma API
        
        Args:
            condition_id: Market condition ID
            
        Returns:
            Market details dictionary
        """
        try:
            response = requests.get(
                f"{self.GAMMA_API}/markets/{condition_id}",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching market {condition_id}: {e}")
            return None
    
    def search_markets(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search markets by keyword
        
        Args:
            query: Search query
            limit: Max results
            
        Returns:
            List of matching markets
        """
        try:
            params = {"query": query, "limit": limit}
            response = requests.get(
                f"{self.GAMMA_API}/markets/search",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error searching markets: {e}")
            return []
    
    def get_events(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get events (groups of related markets)
        
        Args:
            limit: Number of events to return
            
        Returns:
            List of events
        """
        try:
            response = requests.get(
                f"{self.GAMMA_API}/events",
                params={"limit": limit},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching events: {e}")
            return []
    
    # ===== CLOB API: Trading & Orderbooks =====
    
    def get_orderbook(self, token_id: str) -> Dict[str, Any]:
        """
        Get order book for a market token from CLOB API
        
        Args:
            token_id: Token ID for the market outcome
            
        Returns:
            Order book with bids and asks
        """
        try:
            response = requests.get(
                f"{self.CLOB_API}/book",
                params={"token_id": token_id},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching orderbook for {token_id}: {e}")
            return {"bids": [], "asks": []}
    
    def get_price(self, token_id: str) -> Optional[Decimal]:
        """
        Get current mid-market price for a token
        
        Args:
            token_id: Token ID
            
        Returns:
            Current price (0-1 range)
        """
        try:
            orderbook = self.get_orderbook(token_id)
            
            if orderbook.get("bids") and orderbook.get("asks"):
                best_bid = Decimal(str(orderbook["bids"][0]["price"]))
                best_ask = Decimal(str(orderbook["asks"][0]["price"]))
                return (best_bid + best_ask) / 2
            
            return None
        except Exception as e:
            logger.error(f"Error getting price for {token_id}: {e}")
            return None
    
    def place_order(
        self,
        token_id: str,
        side: str,  # "BUY" or "SELL"
        price: Decimal,
        size: Decimal,
        order_type: str = "GTC"  # Good Till Cancelled
    ) -> Optional[Dict[str, Any]]:
        """
        Place an order on Polymarket CLOB
        
        Args:
            token_id: Token ID for the market outcome
            side: "BUY" or "SELL"
            price: Price per share (0-1)
            size: Number of shares
            order_type: Order type (GTC, FOK, IOC)
            
        Returns:
            Order response with order ID
        """
        try:
            if not self.clob_client:
                logger.warning("Cannot place order: CLOB client not configured")
                return None
            
            order_args = OrderArgs(
                token_id=token_id,
                price=float(price),
                size=float(size),
                side=side,
                order_type=order_type
            )
            
            order = self.clob_client.create_order(order_args)
            logger.info(f"Order placed: {order}")
            return order
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return None
    
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an existing order
        
        Args:
            order_id: ID of the order to cancel
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.clob_client:
                return False
            
            self.clob_client.cancel_order(order_id)
            logger.info(f"Order {order_id} cancelled")
            return True
        except Exception as e:
            logger.error(f"Error cancelling order {order_id}: {e}")
            return False
    
    # ===== DATA API: Positions & History =====
    
    def get_positions(self, user_address: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get current positions from Data API
        
        Args:
            user_address: Wallet address (uses authenticated user if None)
            
        Returns:
            List of position dictionaries
        """
        try:
            if not self.clob_client:
                return []
            
            # If using CLOB client, it handles authentication
            positions = self.clob_client.get_positions()
            return positions
        except Exception as e:
            logger.error(f"Error fetching positions: {e}")
            return []
    
    def get_trade_history(
        self,
        user_address: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get trade history from Data API
        
        Args:
            user_address: Wallet address
            limit: Max number of trades
            
        Returns:
            List of trade dictionaries
        """
        try:
            if not user_address:
                return []
            
            response = requests.get(
                f"{self.DATA_API}/trades",
                params={"user": user_address, "limit": limit},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching trade history: {e}")
            return []
    
    def get_balance(self) -> Dict[str, Decimal]:
        """
        Get account balance
        
        Returns:
            Dictionary with balance information
        """
        try:
            if not self.clob_client:
                return {"total": Decimal("0"), "available": Decimal("0")}
            
            balance = self.clob_client.get_balance()
            return {
                "total": Decimal(str(balance.get("total", 0))),
                "available": Decimal(str(balance.get("available", 0)))
            }
        except Exception as e:
            logger.error(f"Error fetching balance: {e}")
            return {"total": Decimal("0"), "available": Decimal("0")}
    
    def _get_sample_markets(self) -> List[Dict[str, Any]]:
        """Return sample markets for demo purposes"""
        return [
            {
                "condition_id": "sample_1",
                "question": "Will Bitcoin reach $100,000 by end of 2024?",
                "description": "Resolves YES if BTC hits $100k, NO otherwise",
                "end_date": "2024-12-31T23:59:59Z",
                "outcomes": ["YES", "NO"],
                "volume": "125000",
                "liquidity": "50000",
                "category": "Crypto"
            },
            {
                "condition_id": "sample_2",
                "question": "Will the S&P 500 be above 5000 in Q1 2024?",
                "description": "Resolves based on closing price on last trading day of Q1",
                "end_date": "2024-03-31T23:59:59Z",
                "outcomes": ["YES", "NO"],
                "volume": "85000",
                "liquidity": "35000",
                "category": "Finance"
            },
            {
                "condition_id": "sample_3",
                "question": "Will AI surpass human performance on benchmark X?",
                "description": "Resolves YES if AI achieves >95% on benchmark",
                "end_date": "2024-06-30T23:59:59Z",
                "outcomes": ["YES", "NO"],
                "volume": "45000",
                "liquidity": "20000",
                "category": "Technology"
            }
        ]


# Global instance
_polymarket_service: Optional[PolymarketService] = None


def get_polymarket_service(
    api_key: Optional[str] = None,
    api_secret: Optional[str] = None,
    api_passphrase: Optional[str] = None
) -> PolymarketService:
    """
    Get or create Polymarket service instance
    
    Args:
        api_key: Polymarket API key (optional)
        api_secret: Polymarket API secret (optional)
        api_passphrase: Polymarket API passphrase (optional)
        
    Returns:
        PolymarketService instance
    """
    global _polymarket_service
    
    if _polymarket_service is None:
        _polymarket_service = PolymarketService(
            api_key=api_key,
            api_secret=api_secret,
            api_passphrase=api_passphrase
        )
    
    return _polymarket_service
