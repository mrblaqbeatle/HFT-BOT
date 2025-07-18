# core/order_manager.py
# Handles sending and monitoring trades via MetaTrader5
import MetaTrader5 as mt5
import logging
import time
from config import CONFIG

class OrderManager:
    def close_position(self, pos):
        order_type = mt5.ORDER_TYPE_SELL if pos.type == mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_BUY
        price = mt5.symbol_info_tick(self.symbol).bid if order_type == mt5.ORDER_TYPE_SELL else mt5.symbol_info_tick(self.symbol).ask
        close_request = {
            'action': mt5.TRADE_ACTION_DEAL,
            'symbol': self.symbol,
            'volume': pos.volume,
            'type': order_type,
            'position': pos.ticket,
            'price': price,
            'deviation': self.slippage,
            'magic': self.magic,
            'comment': self.comment,
            'type_time': mt5.ORDER_TIME_GTC,
            'type_filling': mt5.ORDER_FILLING_IOC,
        }
        for _ in range(3):  # Retry up to 3 times for requotes/errors
            result = mt5.order_send(close_request)
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                logging.info(f"Closed position {pos.ticket}")
                return True
            else:
                logging.error(f"Failed to close position {pos.ticket}: {result.retcode}, retrying...")
                time.sleep(0.01)
        return False
    def __init__(self, symbol):
        self.symbol = symbol
        self.magic = CONFIG['magic_number']
        self.comment = CONFIG['order_comment']
        self.slippage = CONFIG['slippage']

    def send_order(self, direction, lot, sl, tp):
        price = mt5.symbol_info_tick(self.symbol).ask if direction == 'buy' else mt5.symbol_info_tick(self.symbol).bid
        order_type = mt5.ORDER_TYPE_BUY if direction == 'buy' else mt5.ORDER_TYPE_SELL
        request = {
            'action': mt5.TRADE_ACTION_DEAL,
            'symbol': self.symbol,
            'volume': lot,
            'type': order_type,
            'price': price,
            'sl': sl,
            'tp': tp,
            'deviation': self.slippage,
            'magic': self.magic,
            'comment': self.comment,
            'type_time': mt5.ORDER_TIME_GTC,
            'type_filling': mt5.ORDER_FILLING_IOC,
        }
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logging.error(f"Order send failed: {result.retcode} {result.comment}")
            return None
        logging.info(f"Order sent: {direction} {lot} lots at {price}")
        return result

    def get_open_trades(self):
        positions = mt5.positions_get(symbol=self.symbol)
        return positions if positions else []

    def close_all_trades(self):
        positions = self.get_open_trades()
        for pos in positions:
            order_type = mt5.ORDER_TYPE_SELL if pos.type == mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_BUY
            price = mt5.symbol_info_tick(self.symbol).bid if order_type == mt5.ORDER_TYPE_SELL else mt5.symbol_info_tick(self.symbol).ask
            close_request = {
                'action': mt5.TRADE_ACTION_DEAL,
                'symbol': self.symbol,
                'volume': pos.volume,
                'type': order_type,
                'position': pos.ticket,
                'price': price,
                'deviation': self.slippage,
                'magic': self.magic,
                'comment': self.comment,
                'type_time': mt5.ORDER_TIME_GTC,
                'type_filling': mt5.ORDER_FILLING_IOC,
            }
            result = mt5.order_send(close_request)
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                logging.error(f"Failed to close position {pos.ticket}: {result.retcode}")
            else:
                logging.info(f"Closed position {pos.ticket}")
