# core/exit_logic.py
# Ultra-fast exit logic for profit and loss prevention
import time
from config import CONFIG

class ExitLogic:
    def __init__(self):
        self.open_times = {}

    def should_close(self, pos):
        # Profit-targeted exit
        if pos.profit >= CONFIG['MIN_PROFIT_USD']:
            return True
        # Timeout mechanism
        now = time.time()
        open_time = self.open_times.get(pos.ticket, now)
        if pos.profit >= 0 and (now - open_time) * 1000 > CONFIG['TRADE_TIMEOUT_MS']:
            return True
        # Loss prevention: close at breakeven if risk of loss
        if pos.profit < 0:
            return True
        return False

    def register_open(self, pos):
        self.open_times[pos.ticket] = time.time()

    def unregister(self, pos):
        if pos.ticket in self.open_times:
            del self.open_times[pos.ticket]
