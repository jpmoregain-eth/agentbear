"""
CCXT Crypto Trading Tools for ABC AI Agent
Provides cryptocurrency market data and trading via CCXT library
"""

import logging
from typing import Dict, List, Optional
import json

logger = logging.getLogger(__name__)

# Try to import ccxt
try:
    import ccxt
    CCXT_AVAILABLE = True
except ImportError:
    CCXT_AVAILABLE = False
    logger.warning("ccxt not installed. Crypto trading capability disabled.")


class CryptoTools:
    """Cryptocurrency tools powered by CCXT"""
    
    def __init__(self, exchange_id: str = "binance", api_key: str = "", api_secret: str = ""):
        """
        Initialize crypto tools
        
        Args:
            exchange_id: Exchange ID (binance, coinbase, kraken, etc.)
            api_key: API key for the exchange
            api_secret: API secret for the exchange
        """
        if not CCXT_AVAILABLE:
            raise ImportError("ccxt library is required for crypto trading")
        
        self.exchange_id = exchange_id
        self.api_key = api_key
        self.api_secret = api_secret
        self.exchange = None
        
        self._init_exchange()
        logger.info(f"💰 Crypto tools initialized for {exchange_id}")
    
    def _init_exchange(self):
        """Initialize the exchange connection"""
        try:
            exchange_class = getattr(ccxt, self.exchange_id)
            config = {
                'enableRateLimit': True,
            }
            if self.api_key and self.api_secret:
                config['apiKey'] = self.api_key
                config['secret'] = self.api_secret
            
            self.exchange = exchange_class(config)
            self.exchange.load_markets()
            logger.info(f"✅ Connected to {self.exchange_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize exchange: {e}")
            raise
    
    def get_ticker(self, symbol: str = "BTC/USDT") -> Dict:
        """
        Get current price ticker for a symbol
        
        Args:
            symbol: Trading pair (e.g., BTC/USDT, ETH/BTC)
            
        Returns:
            Dict with price data
        """
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return {
                "success": True,
                "symbol": symbol,
                "exchange": self.exchange_id,
                "price": ticker.get('last'),
                "bid": ticker.get('bid'),
                "ask": ticker.get('ask'),
                "high_24h": ticker.get('high'),
                "low_24h": ticker.get('low'),
                "volume_24h": ticker.get('quoteVolume'),
                "change_24h": ticker.get('change'),
                "change_percent_24h": ticker.get('percentage'),
                "timestamp": ticker.get('timestamp')
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch ticker: {e}")
            return {"success": False, "error": str(e)}
    
    def get_ohlcv(self, symbol: str = "BTC/USDT", timeframe: str = "1h", limit: int = 10) -> Dict:
        """
        Get OHLCV (candlestick) data
        
        Args:
            symbol: Trading pair
            timeframe: Time period (1m, 5m, 1h, 4h, 1d, 1w)
            limit: Number of candles
            
        Returns:
            Dict with OHLCV data
        """
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            
            candles = []
            for candle in ohlcv:
                candles.append({
                    "timestamp": candle[0],
                    "open": candle[1],
                    "high": candle[2],
                    "low": candle[3],
                    "close": candle[4],
                    "volume": candle[5]
                })
            
            return {
                "success": True,
                "symbol": symbol,
                "timeframe": timeframe,
                "exchange": self.exchange_id,
                "candles": candles,
                "count": len(candles)
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch OHLCV: {e}")
            return {"success": False, "error": str(e)}
    
    def get_balance(self) -> Dict:
        """
        Get account balance (requires API key)
        
        Returns:
            Dict with balance info
        """
        if not self.api_key:
            return {"success": False, "error": "API key required for balance"}
        
        try:
            balance = self.exchange.fetch_balance()
            
            # Filter non-zero balances
            non_zero = {}
            for currency, data in balance.get('total', {}).items():
                if data and data > 0:
                    non_zero[currency] = data
            
            return {
                "success": True,
                "exchange": self.exchange_id,
                "balances": non_zero,
                "total_currencies": len(non_zero)
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch balance: {e}")
            return {"success": False, "error": str(e)}
    
    def get_supported_symbols(self, quote_currency: str = "USDT") -> Dict:
        """
        Get list of supported trading pairs
        
        Args:
            quote_currency: Filter by quote currency (USDT, BTC, ETH, etc.)
            
        Returns:
            Dict with symbols list
        """
        try:
            symbols = []
            for symbol in self.exchange.symbols:
                if quote_currency in symbol:
                    symbols.append(symbol)
            
            return {
                "success": True,
                "exchange": self.exchange_id,
                "quote_currency": quote_currency,
                "symbols": symbols[:50],  # Limit to 50
                "total": len(symbols)
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch symbols: {e}")
            return {"success": False, "error": str(e)}
    
    def detect_and_execute(self, message: str) -> Optional[Dict]:
        """
        Detect crypto-related commands and execute them
        
        Args:
            message: User message
            
        Returns:
            Result dict if a crypto command was executed
        """
        import re
        msg_lower = message.lower().strip()
        
        # Get price: "price of BTC" or "BTC/USDT price"
        price_patterns = [
            r'(?:price|value|cost)\s+(?:of\s+)?([A-Za-z0-9]+)',
            r'([A-Za-z0-9]+)\s+(?:price|value|cost)',
            r'how\s+much\s+is\s+([A-Za-z0-9]+)',
        ]
        for pattern in price_patterns:
            match = re.search(pattern, msg_lower)
            if match:
                symbol = match.group(1).upper()
                # Add USDT if no quote currency specified
                if '/' not in symbol:
                    symbol = f"{symbol}/USDT"
                return self.get_ticker(symbol)
        
        # Get OHLCV/chart: "chart for BTC" or "BTC candles"
        chart_patterns = [
            r'(?:chart|candles|ohlcv)\s+(?:for\s+)?([A-Za-z0-9]+)',
            r'([A-Za-z0-9]+)\s+(?:chart|candles|ohlcv)',
        ]
        for pattern in chart_patterns:
            match = re.search(pattern, msg_lower)
            if match:
                symbol = match.group(1).upper()
                if '/' not in symbol:
                    symbol = f"{symbol}/USDT"
                # Extract timeframe if mentioned
                tf_match = re.search(r'\b(1m|5m|15m|1h|4h|1d|1w)\b', msg_lower)
                timeframe = tf_match.group(1) if tf_match else "1h"
                return self.get_ohlcv(symbol, timeframe)
        
        # Get balance: "my balance" or "show balance"
        if 'balance' in msg_lower and ('my' in msg_lower or 'show' in msg_lower):
            return self.get_balance()
        
        # List symbols: "list coins" or "supported pairs"
        if any(phrase in msg_lower for phrase in ['list coins', 'supported pairs', 'available symbols']):
            quote = "USDT"
            # Try to extract quote currency
            quote_match = re.search(r'in\s+([A-Z]{2,5})', message.upper())
            if quote_match:
                quote = quote_match.group(1)
            return self.get_supported_symbols(quote)
        
        return None


# For testing
if __name__ == "__main__":
    # Test without API key (public data only)
    print("Testing CryptoTools with Binance...")
    try:
        tools = CryptoTools(exchange_id="binance")
        
        print("\nTesting get_ticker...")
        result = tools.get_ticker("BTC/USDT")
        if result.get('success'):
            print(f"BTC Price: ${result['price']}")
        else:
            print(f"Error: {result.get('error')}")
        
        print("\nTesting get_ohlcv...")
        result = tools.get_ohlcv("BTC/USDT", "1h", 5)
        if result.get('success'):
            print(f"Got {result['count']} candles")
        
        print("\n✅ Crypto tools test completed!")
        
    except Exception as e:
        print(f"Test failed: {e}")
