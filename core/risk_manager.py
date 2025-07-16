# core/risk_manager.py
# Calculates SL/TP, lot size, max loss, and handles exits
import MetaTrader5 as mt5
from config import CONFIG
import logging

class RiskManager:
    def __init__(self, symbol):
        self.symbol = symbol
        self.stop_loss_usd = CONFIG['stop_loss_usd']
        self.lot_size = CONFIG['lot_size']

    def calc_sl_tp(self, direction, entry_price):
        """
        Calculate SL/TP in price based on USD risk and reward.
        """
        symbol_info = mt5.symbol_info(self.symbol)
        point = symbol_info.point
        # Estimate pip value for 0.01 lot
        pip_value = symbol_info.trade_tick_value
        if pip_value == 0:
            pip_value = 1
        sl_points = int(self.stop_loss_usd / (pip_value * self.lot_size))
        if sl_points < 5:
            sl_points = 5
        if direction == 'buy':
            sl = entry_price - sl_points * point
            tp = entry_price + (self.stop_loss_usd * 2 / (pip_value * self.lot_size)) * point
        else:
            sl = entry_price + sl_points * point
            tp = entry_price - (self.stop_loss_usd * 2 / (pip_value * self.lot_size)) * point
        return round(sl, symbol_info.digits), round(tp, symbol_info.digits)

    def check_max_loss(self, daily_loss):
        if daily_loss >= CONFIG['max_daily_loss']:
            logging.warning("Max daily loss reached. Stopping trading.")
            return True
        return False
