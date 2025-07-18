# config.py
# User-configurable settings for the MT5 scalping bot

CONFIG = {
    'symbol': 'EURUSD',
    'lot_size': 0.01,
    'profit_target_usd': 5.0,
    'MIN_TICK_DISTANCE': 5,           # Minimum price change (points) before new entry
    'TICK_VELOCITY_WINDOW': 5,        # Number of ticks for momentum calculation
    'SPREAD_THRESHOLD': 3,            # Maximum spread (points) for trade entry
    'MIN_PROFIT_USD': 0.01,           # Minimum profit (USD) to exit trade
    'TRADE_TIMEOUT_MS': 500,          # Maximum time (ms) for breakeven exit
    'ENTRY_THROTTLE_MS': 100,         # Minimum time (ms) between trades
    'MAX_TRADES': 5,                  # Maximum simultaneous trades
    'TICK_VOLUME_THRESHOLD': 10,      # Minimum tick volume for liquidity check
    'slippage': 5,
    'magic_number': 123456,
    'order_comment': 'XOXO_HFT',
    'max_daily_loss': 5.0,
}
