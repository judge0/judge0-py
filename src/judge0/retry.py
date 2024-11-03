import time
from abc import ABC, abstractmethod


class RetryMechanism(ABC):
    @abstractmethod
    def is_done(self) -> bool:
        pass

    @abstractmethod
    def wait(self) -> None:
        pass

    @abstractmethod
    def step(self) -> None:
        pass


class MaxRetries(RetryMechanism):
    """Check for submissions status every 100 ms and retry a maximum of
    `max_retries` times."""

    def __init__(self, max_retries: int = 20):
        self.n_retries = 0
        self.max_retries = max_retries

    def step(self):
        self.n_retries += 1

    def wait(self):
        time.sleep(0.1)

    def is_done(self) -> bool:
        return self.n_retries >= self.max_retries


class MaxWaitTime(RetryMechanism):
    """Check for submissions status every 100 ms and wait for all submissions
    a maximum of `max_wait_time` (seconds)."""

    def __init__(self, max_wait_time_sec: float = 5 * 60):
        self.max_wait_time_sec = max_wait_time_sec
        self.total_wait_time = 0

    def step(self):
        self.total_wait_time += 0.1

    def wait(self):
        time.sleep(0.1)

    def is_done(self):
        return self.total_wait_time >= self.max_wait_time_sec


class RegularPeriodRetry(RetryMechanism):
    """Check for submissions status periodically for indefinite amount of time."""

    def __init__(self, wait_time_sec: float = 0.1):
        self.wait_time_sec = wait_time_sec

    def step(self):
        pass

    def wait(self):
        time.sleep(self.wait_time_sec)

    def is_done(self) -> bool:
        return False
