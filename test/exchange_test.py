# src/exchange_mock.py
import random
import time


class ExchangeWrapperMock:
    def __init__(self, config_file='../config/config.json'):
        self.config = {
            "symbol": "BTC/USDT",
            "refresh_interval": 60
        }
        self.current_price = 50000  # Price

    def get_market_price(self):
        """ Simolation network """
        self.current_price *= (1 + random.uniform(-0.005,
                               0.005))  # ±0.5%
        return round(self.current_price, 2)

    def place_orders(self, bids, asks):
        """ Simolation order """

        print("\n--- Orders Placed ---")
        print(f"Current Price: {self.current_price:.2f}")
        print("Bids (Buy Orders):")
        for price, amount in bids:
            print(f"  {amount} BTC @ {price:.2f}")
        print("Asks (Sell Orders):")
        for price, amount in asks:
            print(f"  {amount} BTC @ {price:.2f}")
        return True
