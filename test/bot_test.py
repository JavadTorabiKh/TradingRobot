import json
import time
import logging
from exchange_test import ExchangeWrapperMock
from market_maker_test import MarketMaker

# Configure logging
logging.basicConfig(
    filename='../logs/bot.log',  # Log file location
    level=logging.INFO,          # Logging level
    format='%(asctime)s - %(levelname)s - %(message)s'  # Log format
)


def main():
    """Main execution function for the trading bot"""
    try:
        # Initialize exchange connection
        exchange = ExchangeWrapperMock()
        # Initialize market making strategy
        market_maker = MarketMaker(exchange)

        logging.info("Starting trading bot...")

        # Main trading loop
        while True:
            try:
                # Get current market price
                price = exchange.get_market_price()
                if price is None:
                    continue  # Skip iteration if price fetch failed

                # Calculate bid/ask orders
                bids, asks = market_maker.calculate_orders(price)

                # Place orders on exchange
                if exchange.place_orders(bids, asks):
                    logging.info(
                        f"Orders updated | Price: {price:.2f} | "
                        f"Bids: {len(bids)} | Asks: {len(asks)}"
                    )

                # Wait for next iteration
                time.sleep(exchange.config['refresh_interval'])

            except KeyboardInterrupt:
                logging.info("Bot stopped by user")
                break
            except Exception as e:
                logging.error(f"Error in main loop: {e}")
                time.sleep(10)  # Wait before retry

    except Exception as e:
        logging.critical(f"Fatal error: {e}")


if __name__ == "__main__":
    main()  # Start the bot
