import time

import django.core.cache


class UserRateThrottle:
    def __init__(self, rate=10, period=10):
        self.rate = rate
        self.period = period

    def allow_request(self, user_id):
        current_time = time.time()
        cache_key = f"user_socket_requests_{user_id}"

        timestamps = django.core.cache.cache.get(cache_key, [])

        timestamps = [
            timestamp
            for timestamp in timestamps
            if current_time - timestamp < self.period
        ]

        if len(timestamps) < self.rate:
            timestamps.append(current_time)
            django.core.cache.cache.set(
                cache_key, timestamps, timeout=self.period
            )
            return True

        return False
