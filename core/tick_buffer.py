# core/tick_buffer.py
# In-memory buffer for high-frequency tick data and velocity calculations
import collections
import time

class TickBuffer:
    def __init__(self, window=5):
        self.window = window
        self.buffer = collections.deque(maxlen=window)
        self.last_tick_time = 0

    def add_tick(self, bid, ask, volume):
        self.buffer.append({'bid': bid, 'ask': ask, 'volume': volume, 'time': time.time()})
        self.last_tick_time = time.time()

    def get_velocity(self):
        if len(self.buffer) < 2:
            return 0, 0
        bids = [tick['bid'] for tick in self.buffer]
        asks = [tick['ask'] for tick in self.buffer]
        bid_velocity = bids[-1] - bids[0]
        ask_velocity = asks[-1] - asks[0]
        return bid_velocity, ask_velocity

    def get_spread(self):
        if not self.buffer:
            return 0
        return self.buffer[-1]['ask'] - self.buffer[-1]['bid']

    def get_tick_volume(self):
        if not self.buffer:
            return 0
        return self.buffer[-1]['volume']

    def last_tick(self):
        return self.buffer[-1] if self.buffer else None
