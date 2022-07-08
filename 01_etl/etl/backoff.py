import time
from functools import wraps
import logging

def backoff(start_sleep_time=0.1, factor=2, border_sleep_time=10):
    """
    Функция для повторного выполнения функции через некоторое время, если возникла ошибка.
    """
    def func_wrapper(func):

        @wraps(func)
        def inner(*args, **kwargs):
            next_sleep_time = start_sleep_time
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception:
                    logging.debug("Backoff столкнулся с ошибкой")
                    time.sleep(next_sleep_time)
                    if next_sleep_time >= border_sleep_time:
                        next_sleep_time = border_sleep_time
                    else:
                        next_sleep_time *= factor
        return inner
    return func_wrapper

# psycopg2.OperationalError