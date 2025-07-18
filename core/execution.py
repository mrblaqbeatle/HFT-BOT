# core/execution.py
# Trade execution and management for HFT bot
import MetaTrader5 as mt5
import logging
from config import CONFIG

class Execution:
    def __init__(self, symbol):
        self.symbol = symbol
        self.volume = CONFIG['TRADE_VOLUME']
        self.slippage = CONFIG.get('SLIPPAGE', 5)
        self.magic = CONFIG.get('MAGIC_NUMBER', 123456)
        self.comment = CONFIG.get('ORDER_COMMENT', 'XOXO_HFT')

    def place_buy(self):
        price = mt5.symbol_info_tick(self.symbol).ask
        request = {
            'action': mt5.TRADE_ACTION_DEAL,
            'symbol': self.symbol,
            'volume': self.volume,
            'type': mt5.ORDER_TYPE_BUY,
            'price': price,
            'deviation': self.slippage,
            'magic': self.magic,
            'comment': self.comment,
            'type_time': mt5.ORDER_TIME_GTC,
            'type_filling': mt5.ORDER_FILLING_IOC,
        }
        result = mt5.order_send(request)
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            logging.info(f"BUY order placed at {price}")
            return result
        else:
            logging.error(f"BUY order failed: {result.retcode}")
            return None

    def place_sell(self):
        price = mt5.symbol_info_tick(self.symbol).bid
        request = {
            'action': mt5.TRADE_ACTION_DEAL,
            'symbol': self.symbol,
            'volume': self.volume,
            'type': mt5.ORDER_TYPE_SELL,
            'price': price,
            'deviation': self.slippage,
            'magic': self.magic,
            'comment': self.comment,
            'type_time': mt5.ORDER_TIME_GTC,
            'type_filling': mt5.ORDER_FILLING_IOC,
        }
        result = mt5.order_send(request)
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            logging.info(f"SELL order placed at {price}")
            return result
        else:
            logging.error(f"SELL order failed: {result.retcode}")
            return None

    def close_order(self, ticket):
        positions = mt5.positions_get(ticket=ticket)
        if not positions:
            return False
        pos = positions[0]
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
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            logging.info(f"Closed order {ticket}")
            return True
        else:
            logging.error(f"Failed to close order {ticket}: {result.retcode}")
            return False

    def get_active_trades(self):
        return mt5.positions_get(symbol=self.symbol) or []
