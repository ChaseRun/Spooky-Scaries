from time import time
from datetime import timedelta

def print_runtime(func):
    def decorator():
        start_time = time()
        func()
        end_time = timedelta(seconds=round(time() - start_time))
        format_end_time = f"Execution Time: {end_time} (HH:MM:SS)"
        print(format_end_time)
    return decorator