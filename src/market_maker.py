import json


class MarketMaker:
    """
    Market Making Strategy Class
    Calculates order prices and sizes based on market conditions
    """

    def __init__(self, exchange, config_file='./config/config.json'):
        """Initialize with exchange instance and config"""
        self.exchange = exchange  # ExchangeWrapper instance
        with open(config_file) as f:
            self.config = json.load(f)  # Load configuration

    def calculate_orders(self, current_price):
        """
        Calculate bid and ask orders based on current price
        Args:
            current_price (float): Current market price
        Returns:
            tuple: (bids, asks) where each is a list of (price, amount) tuples
        """
        spread = self.config['spread']  # Get spread from config
        order_size = self.config['order_size']  # Base order size
        max_orders = self.config['max_orders']  # Number of orders per side

        bids = []  # Buy orders
        asks = []  # Sell orders

        for i in range(max_orders):
            # Calculate bid price (below market)
            bid_price = round(current_price * (1 - (spread/2) * (i + 1)), 2)
            bids.append((bid_price, order_size))

            # Calculate ask price (above market)
            ask_price = round(current_price * (1 + (spread/2) * (i + 1)), 2)
            asks.append((ask_price, order_size))

        return bids, asks
