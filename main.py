# main.py
# Entry point for the MT5 scalping bot
import MetaTrader5 as mt5
import logging
import time
from config import CONFIG
from core.order_manager import OrderManager
from core.risk_manager import RiskManager
from core.profit_monitor import ProfitMonitor

logging.basicConfig(
    format='%(asctime)s %(levelname)s: %(message)s',
    level=logging.INFO
)

def main():
    logging.info("Starting XOXO Flipper Scalping Bot...")
    if not mt5.initialize():
        logging.error(f"MT5 initialization failed: {mt5.last_error()}")
        return
    symbol = CONFIG['symbol']
    if not mt5.symbol_select(symbol, True):
        logging.error(f"Symbol {symbol} not found or not available.")
        mt5.shutdown()
        return
    order_mgr = OrderManager(symbol)
    risk_mgr = RiskManager(symbol)
    profit_mon = ProfitMonitor(symbol)
    logging.info(f"Bot initialized for {symbol}.")
    try:
        last_status = time.time()
        while True:
            if time.time() - last_status > 2:
                logging.info("[ACTIVE] HFT flipping: monitoring, entering, and closing trades...")
                last_status = time.time()

            symbol_info = mt5.symbol_info(symbol)
            spread = symbol_info.spread
            if spread < CONFIG['min_spread'] or spread > CONFIG['max_spread']:
                time.sleep(0.05)
                continue

            open_trades = order_mgr.get_open_trades()
            # Close all trades that are in profit immediately
            for pos in open_trades:
                if pos.profit > 0:
                    order_mgr.close_position(pos)
                    logging.info(f"[CLOSE] Closed ticket {pos.ticket} for profit: {pos.profit:.2f}")

            # Check if profit target is hit
            if profit_mon.check_profit_target():
                order_mgr.close_all_trades()
                logging.info("Bot stopping for the day.")
                break

            # If we can open more trades, open both a buy and a sell (flipping both ways)
            if len(open_trades) < CONFIG['max_open_trades']:
                # Open both directions for maximum flipping
                price_ask = mt5.symbol_info_tick(symbol).ask
                price_bid = mt5.symbol_info_tick(symbol).bid
                sl_buy, tp_buy = risk_mgr.calc_sl_tp('buy', price_ask)
                sl_sell, tp_sell = risk_mgr.calc_sl_tp('sell', price_bid)
                result_buy = order_mgr.send_order('buy', CONFIG['lot_size'], sl_buy, tp_buy)
                if result_buy:
                    logging.info(f"[OPEN] BUY at {price_ask}")
                result_sell = order_mgr.send_order('sell', CONFIG['lot_size'], sl_sell, tp_sell)
                if result_sell:
                    logging.info(f"[OPEN] SELL at {price_bid}")

            time.sleep(0.05)
    except Exception as e:
        logging.error(f"Exception: {e}")
    finally:
        mt5.shutdown()
        logging.info("MT5 connection closed. Bot exited.")

if __name__ == '__main__':
    main()
