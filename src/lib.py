import random
import time
def random_sleep(n):
    """Sleep for a random duration between 0.5n and 1.5n seconds."""
    duration = random.uniform(0.5 * n, 1.5 * n)
    time.sleep(duration)

