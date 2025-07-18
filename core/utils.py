# core/utils.py
# Utilities for tick velocity and momentum detection
import time

def get_tick_velocity(tick_buffer):
    if len(tick_buffer) < 2:
        return 0, 0, 0
    t1 = tick_buffer[-2]['time']
    t2 = tick_buffer[-1]['time']
    dt = t2 - t1 if t2 > t1 else 1e-6
    bid_vel = (tick_buffer[-1]['bid'] - tick_buffer[-2]['bid']) / dt
    ask_vel = (tick_buffer[-1]['ask'] - tick_buffer[-2]['ask']) / dt
    return bid_vel, ask_vel, dt

def is_momentum_up(tick_buffer, threshold=0.00005):
    bid_vel, ask_vel, _ = get_tick_velocity(tick_buffer)
    return ask_vel > threshold

def is_momentum_down(tick_buffer, threshold=0.00005):
    bid_vel, ask_vel, _ = get_tick_velocity(tick_buffer)
    return bid_vel < -threshold
