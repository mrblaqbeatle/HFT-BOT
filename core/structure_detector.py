# core/structure_detector.py
# Detects price action-based entries (no classic indicators)
import MetaTrader5 as mt5
import logging
from config import CONFIG

class StructureDetector:
    def __init__(self, symbol):
        self.symbol = symbol
        self.timeframe = getattr(mt5, f'TIMEFRAME_{CONFIG["timeframe"]}')
        self.history_bars = CONFIG['history_bars']

    def get_recent_bars(self):
        rates = mt5.copy_rates_from_pos(self.symbol, self.timeframe, 0, self.history_bars)
        return rates

    def detect_entry(self):
        """
        Example logic: Detects micro break of structure (BOS) and liquidity sweep.
        - Looks for a strong engulfing candle after a sweep of recent highs/lows.
        - Returns 'buy', 'sell', or None.
        """
        bars = self.get_recent_bars()
        if bars is None or len(bars) < 10:
            return None
        highs = [b['high'] for b in bars]
        lows = [b['low'] for b in bars]
        close = [b['close'] for b in bars]
        open_ = [b['open'] for b in bars]
        # Detect liquidity sweep (price wicks above/below recent high/low then reverses)
        recent_high = max(highs[-10:-1])
        recent_low = min(lows[-10:-1])
        last_bar = bars[-1]
        prev_bar = bars[-2]
        # Bullish sweep and engulf
        if last_bar['low'] < recent_low and last_bar['close'] > prev_bar['high']:
            return 'buy'
        # Bearish sweep and engulf
        if last_bar['high'] > recent_high and last_bar['close'] < prev_bar['low']:
            return 'sell'
        return None
