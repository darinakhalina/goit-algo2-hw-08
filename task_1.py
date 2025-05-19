import random
from typing import Dict
import time
from collections import deque


class SlidingWindowRateLimiter:
    def __init__(self, window_size=10, max_requests=1):
        self.window_size = window_size
        self.max_requests = max_requests
        self.messages: Dict[str, deque] = {}

    def _cleanup_window(self, user_id: str, current_time: float) -> None:
        if user_id not in self.messages:
            return

        time_deque = self.messages[user_id]
        while time_deque and (current_time - time_deque[0]) > self.window_size:
            time_deque.popleft()

        if not time_deque:
            del self.messages[user_id]

    def can_send_message(self, user_id: str) -> bool:
        now = time.time()
        self._cleanup_window(user_id, now)

        if user_id not in self.messages:
            return True
        if len(self.messages[user_id]) < self.max_requests:
            return True
        return False

    def record_message(self, user_id: str) -> bool:
        if self.can_send_message(user_id):
            now = time.time()
            if user_id not in self.messages:
                self.messages[user_id] = deque()
            self.messages[user_id].append(now)
            return True
        return False

    def time_until_next_allowed(self, user_id: str) -> float:
        now = time.time()
        self._cleanup_window(user_id, now)

        if user_id not in self.messages:
            return 0.0

        if len(self.messages[user_id]) < self.max_requests:
            return 0.0

        oldest_time = self.messages[user_id][0]
        next_allowed = oldest_time + self.window_size
        wait_time = next_allowed - now
        return max(0.0, wait_time)


def test_rate_limiter():
    # Створюємо rate limiter: вікно 10 секунд, 1 повідомлення
    limiter = SlidingWindowRateLimiter(window_size=10, max_requests=1)

    # Симулюємо потік повідомлень від користувачів (ID від 1 до 5)
    print("\n=== Симуляція потоку повідомлень (Sliding Window) ===")
    for message_id in range(1, 11):
        user_id = message_id % 5 + 1

        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))

        print(
            f"Повідомлення {message_id:2d} | Користувач {user_id} | "
            f"{'✓' if result else f'× (очікування %.1fс)' % wait_time}"
        )

        # Невелика затримка між повідомленнями для реалістичності
        # Випадкова затримка від 0.1 до 1 секунди
        time.sleep(random.uniform(0.1, 1.0))

    # Чекаємо, поки вікно очиститься
    print("\nОчікуємо 4 секунди...")
    time.sleep(4)

    print("\n=== Нова серія повідомлень після очікування ===")
    for message_id in range(11, 21):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))

        print(
            f"Повідомлення {message_id:2d} | Користувач {user_id} | "
            f"{'✓' if result else f'× (очікування %.1fс)' % wait_time}"
        )

        time.sleep(random.uniform(0.1, 1.0))


if __name__ == "__main__":
    test_rate_limiter()
