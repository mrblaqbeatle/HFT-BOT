# main.py
# Entry point for the MT5 scalping bot
import MetaTrader5 as mt5
import logging
import time
from config import CONFIG
from core.order_manager import OrderManager
from core.risk_manager import RiskManager
from core.profit_monitor import ProfitMonitor
from core.tick_buffer import TickBuffer
from core.entry_logic import EntryLogic
from core.exit_logic import ExitLogic

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
    tick_buffer = TickBuffer(window=CONFIG['TICK_VELOCITY_WINDOW'])
    entry_logic = EntryLogic(tick_buffer)
    exit_logic = ExitLogic()
    logging.info(f"Bot initialized for {symbol}.")
    try:
        last_status = time.time()
        while True:
            # Get latest tick
            tick = mt5.symbol_info_tick(symbol)
            tick_buffer.add_tick(tick.bid, tick.ask, tick.volume)
            # Frequent status log
            if time.time() - last_status > 2:
                logging.info("[ACTIVE] HFT: monitoring, entering, and closing trades...")
                last_status = time.time()
            # Check open trades
            open_trades = order_mgr.get_open_trades()
            # Exit logic: close trades with profit, timeout, or loss prevention
            for pos in open_trades:
                if pos.ticket not in exit_logic.open_times:
                    exit_logic.register_open(pos)
                if exit_logic.should_close(pos):
                    order_mgr.close_position(pos)
                    exit_logic.unregister(pos)
                    logging.info(f"[CLOSE] Closed ticket {pos.ticket} for profit: {pos.profit:.2f}")
            # Check if profit target is hit
            if profit_mon.check_profit_target():
                order_mgr.close_all_trades()
                logging.info("Bot stopping for the day.")
                break
            # Entry logic: only enter if high-probability signal
            if len(open_trades) < CONFIG['MAX_TRADES']:
                signal = entry_logic.can_enter_trade()
                if signal:
                    price = tick.ask if signal == 'buy' else tick.bid
                    sl, tp = risk_mgr.calc_sl_tp(signal, price)
                    result = order_mgr.send_order(signal, CONFIG['lot_size'], sl, tp)
                    if result:
                        logging.info(f"[OPEN] {signal.upper()} at {price}")
            time.sleep(0.01)
    except Exception as e:
        logging.error(f"Exception: {e}")
    finally:
        mt5.shutdown()
        logging.info("MT5 connection closed. Bot exited.")

if __name__ == '__main__':
    main()
