import ccxt
import json
import time


class ExchangeWrapper:
    """
    CCXT Exchange Wrapper Class
    Handles all exchange communication and order management
    """

    def __init__(self, config_file='../config/config.json'):
        """Initialize exchange connection with config"""
        with open(config_file) as f:
            self.config = json.load(f)  # Load configuration

        # Initialize CCXT exchange instance
        self.exchange = getattr(ccxt, self.config['exchange'])({
            'apiKey': self.config['api_key'],
            'secret': self.config['api_secret'],
            'enableRateLimit': True  # Enable rate limiting
        })
        self.symbol = self.config['symbol']  # Trading pair

    def get_market_price(self):
        """
        Fetch current market price
        Returns:
            float: Last traded price or None if error occurs
        """
        try:
            ticker = self.exchange.fetch_ticker(self.symbol)
            return ticker['last']  # Return last traded price
        except Exception as e:
            print(f"Error getting price: {e}")
            time.sleep(5)  # Wait before retry
            return None

    def place_orders(self, bids, asks):
        """
        Place limit orders on exchange
        Args:
            bids: List of (price, amount) tuples for buy orders
            asks: List of (price, amount) tuples for sell orders
        Returns:
            bool: True if orders placed successfully, False otherwise
        """
        try:
            # Cancel all existing orders first
            self.exchange.cancel_all_orders(self.symbol)

            # Place new buy orders
            for price, amount in bids:
                self.exchange.create_limit_buy_order(
                    self.symbol,
                    amount,
                    price
                )

            # Place new sell orders
            for price, amount in asks:
                self.exchange.create_limit_sell_order(
                    self.symbol,
                    amount,
                    price
                )

            return True
        except Exception as e:
            print(f"Error placing orders: {e}")
            return False
