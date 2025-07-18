# core/entry_logic.py
# High-probability entry logic using tick velocity and microstructure
import time
from config import CONFIG

class EntryLogic:
    def __init__(self, tick_buffer):
        self.tick_buffer = tick_buffer
        self.last_entry_time = 0
        self.last_entry_price = None

    def can_enter_trade(self):
        tick = self.tick_buffer.last_tick()
        if not tick:
            return None
        spread = self.tick_buffer.get_spread()
        tick_volume = self.tick_buffer.get_tick_volume()
        bid_velocity, ask_velocity = self.tick_buffer.get_velocity()
        now = time.time()
        # Spread filter
        if spread > CONFIG['SPREAD_THRESHOLD']:
            return None
        # Tick volume filter
        if tick_volume < CONFIG['TICK_VOLUME_THRESHOLD']:
            return None
        # Entry throttle
        if now - self.last_entry_time < CONFIG['ENTRY_THROTTLE_MS'] / 1000.0:
            return None
        # Price proximity filter
        if self.last_entry_price is not None and abs(tick['ask'] - self.last_entry_price) < CONFIG['MIN_TICK_DISTANCE'] * 0.0001:
            return None
        # Directional momentum logic
        if ask_velocity > 0 and abs(ask_velocity) > abs(bid_velocity):
            self.last_entry_time = now
            self.last_entry_price = tick['ask']
            return 'buy'
        elif bid_velocity < 0 and abs(bid_velocity) > abs(ask_velocity):
            self.last_entry_time = now
            self.last_entry_price = tick['bid']
            return 'sell'
        return None
