# core/profit_monitor.py
# Tracks total daily PnL and triggers close-all when target is hit
import MetaTrader5 as mt5
import logging
from config import CONFIG
from datetime import datetime

class ProfitMonitor:
    def __init__(self, symbol):
        self.symbol = symbol
        self.profit_target = CONFIG['profit_target_usd']
        self.max_daily_loss = CONFIG['max_daily_loss']
        self.today = datetime.now().date()

    def get_daily_pnl(self):
        deals = mt5.history_deals_get(datetime.combine(self.today, datetime.min.time()), datetime.now())
        profit = 0.0
        if deals:
            for d in deals:
                if d.symbol == self.symbol:
                    profit += d.profit
        return profit

    def check_profit_target(self):
        pnl = self.get_daily_pnl()
        if pnl >= self.profit_target:
            logging.info(f"Daily profit target reached: ${pnl:.2f}")
            return True
        if pnl <= -self.max_daily_loss:
            logging.warning(f"Max daily loss reached: ${pnl:.2f}")
            return True
        return False
