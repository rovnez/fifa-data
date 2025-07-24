# rate_limiter.py
import time
import random
import threading


class TokenBucket:
    def __init__(self, rate_per_sec=1 / 0.3, capacity=1):
        self.rate = rate_per_sec
        self.capacity = capacity
        self.tokens = capacity
        self.timestamp = time.monotonic()
        self.lock = threading.Lock()

    def acquire(self):
        with self.lock:
            now = time.monotonic()
            delta = now - self.timestamp
            self.timestamp = now
            self.tokens = min(self.capacity, self.tokens + delta * self.rate)
            if self.tokens < 1:
                sleep_time = (1 - self.tokens) / self.rate
                time.sleep(sleep_time)
                self.tokens = 0
                self.timestamp = time.monotonic()
            self.tokens -= 1


def polite_sleep(mean, jitter):
    return time.sleep(max(0, random.uniform(mean - jitter, mean + jitter)))
