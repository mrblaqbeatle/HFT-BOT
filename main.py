# main.py
# Entry point for the MT5 scalping bot
import MetaTrader5 as mt5
import logging
import time
from config import CONFIG
from core.execution import Execution
from core.utils import get_tick_velocity, is_momentum_up, is_momentum_down
import collections

logging.basicConfig(
    format='%(asctime)s %(levelname)s: %(message)s',
    level=logging.INFO
)

def main():
    logging.info("Starting XOXO Flipper Scalping Bot...")
    if not mt5.initialize():
        logging.error(f"MT5 initialization failed: {mt5.last_error()}")
        return
    symbol = CONFIG['SYMBOL']
    if not mt5.symbol_select(symbol, True):
        logging.error(f"Symbol {symbol} not found or not available.")
        mt5.shutdown()
        return
    exec_engine = Execution(symbol)
    tick_buffer = collections.deque(maxlen=CONFIG['TICK_VELOCITY_WINDOW'])
    last_trade_time = 0
    daily_profit = 0.0
    zero_profit_count = 0
    logging.info(f"Bot initialized for {symbol}.")
    try:
        last_status = time.time()
        while True:
            tick = mt5.symbol_info_tick(symbol)
            tick_buffer.append({'bid': tick.bid, 'ask': tick.ask, 'volume': tick.volume, 'time': time.time()})
            # Frequent status log
            if time.time() - last_status > 2:
                logging.info("[ACTIVE] HFT: monitoring, entering, and closing trades...")
                last_status = time.time()
            # Get active trades
            active_trades = exec_engine.get_active_trades()
            # Exit logic: close trades with profit
            for pos in active_trades:
                if pos.profit >= CONFIG['MIN_PROFIT_USD']:
                    exec_engine.close_order(pos.ticket)
                    daily_profit += pos.profit
                    logging.info(f"[CLOSE] Closed ticket {pos.ticket} for profit: {pos.profit:.2f}")
                    if pos.profit == 0:
                        zero_profit_count += 1
                    else:
                        zero_profit_count = 0
            # Fail-safe: pause if >3 zero-profit trades in a row
            if zero_profit_count > 3:
                logging.warning("Pausing for 5 seconds due to consecutive zero-profit trades.")
                time.sleep(5)
                zero_profit_count = 0
            # Check if daily profit target is hit
            if daily_profit >= CONFIG['DAILY_PROFIT_TARGET']:
                for pos in exec_engine.get_active_trades():
                    exec_engine.close_order(pos.ticket)
                logging.info("Bot stopping for the day. Daily profit target reached.")
                break
            # Entry logic: only enter if micro-momentum detected and not overtrading
            if len(active_trades) < CONFIG['MAX_SIMULTANEOUS_TRADES']:
                bid_vel, ask_vel, dt = get_tick_velocity(tick_buffer)
                spread = tick.ask - tick.bid
                if spread <= CONFIG['SPREAD_THRESHOLD'] * 0.0001:
                    now = time.time()
                    if now - last_trade_time >= CONFIG['CHECK_INTERVAL_MS'] / 1000.0:
                        if is_momentum_up(tick_buffer):
                            result = exec_engine.place_buy()
                            if result:
                                last_trade_time = now
                                logging.info(f"[OPEN] BUY at {tick.ask}")
                        elif is_momentum_down(tick_buffer):
                            result = exec_engine.place_sell()
                            if result:
                                last_trade_time = now
                                logging.info(f"[OPEN] SELL at {tick.bid}")
            time.sleep(CONFIG['CHECK_INTERVAL_MS'] / 1000.0)
    except Exception as e:
        logging.error(f"Exception: {e}")
    finally:
        mt5.shutdown()
        logging.info("MT5 connection closed. Bot exited.")

if __name__ == '__main__':
    main()
