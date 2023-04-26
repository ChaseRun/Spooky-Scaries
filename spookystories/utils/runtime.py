from functools import wraps

from time import time
from datetime import timedelta

# TODO:
# generate - Execution Time: 1.0830555555555557 Hours, 64.98333333333333 Minutes, and 3899 Seconds
def print_runtime(func):
    def decorator(*args, **kwargs):
        start_time = time()
        func(*args, **kwargs)
        end_time = time()

        sec = timedelta(seconds=round(end_time - start_time)).seconds
        min = sec / 60
        hours = sec / (60 * 60)

        time_str = ""
        if hours == 1:
            time_str += f"1 Hour, "
        if hours > 1:
            time_str += f"{hours} Hours, "
        if min == 1:
            time_str += f"1 Minute, "
        if min > 1:
            time_str += f"{min} Minutes, "
        if sec == 1:
            time_str += f"and 1 Second"
        if sec > 1:
            time_str += f"and {sec} Seconds"

        if time_str.startswith("and "):
            time_str = time_str[len("and "):]
        if time_str.endswith(", "):
            time_str = time_str[:len(", ")]

        print(f"{func.__name__} - Execution Time: {time_str}")
    return decorator