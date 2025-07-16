# config.py
# User-configurable settings for the MT5 scalping bot

CONFIG = {
    'symbol': 'EURUSD',            # Trading symbol
    'lot_size': 0.01,              # Default lot size
    'profit_target_usd': 5.0,      # Daily profit target in USD
    'stop_loss_usd': 2.0,          # Optional stop loss per trade in USD
    'max_open_trades': 10,          # Max simultaneous open trades
    'slippage': 5,                 # Max slippage in points
    'magic_number': 123456,        # Magic number for identifying bot trades
    'order_comment': 'XOXO_FLIP',  # Order comment for tracking
    'max_daily_loss': 5.0,         # Optional: max daily loss before shutdown
    'timeframe': 'M1',             # Timeframe for price action (1-min)
    'history_bars': 100,           # Number of bars to analyze for structure
    'min_spread': 0,               # Minimum spread allowed (in points)
    'max_spread': 30,              # Maximum spread allowed (in points)
    'trade_timeout_sec': 60,       # Timeout for order execution
}
