import unittest
import time
from src.rules import BehaviorEngine

class TestBehaviorEngine(unittest.TestCase):
    def test_loitering(self):
        eng = BehaviorEngine(loitering_seconds=2, shelf_exit_repeat_count=2, shelf_exit_time_window_seconds=60)
        pid = 1
        t0 = time.time()
        # Enter shelf
        triggers = eng.update(pid, "shelf", now=t0)
        self.assertEqual(triggers, [])
        # After threshold
        triggers = eng.update(pid, "shelf", now=t0 + 2.1)
        self.assertIn("Loitering in Shelf Zone", triggers)

    def test_exit_without_checkout(self):
        eng = BehaviorEngine(loitering_seconds=100, shelf_exit_repeat_count=2, shelf_exit_time_window_seconds=60)
        pid = 2
        t0 = time.time()
        eng.update(pid, "shelf", now=t0)
        triggers = eng.update(pid, "exit", now=t0 + 5)
        self.assertIn("Exit Without Checkout", triggers)

    def test_repeated_shelf_exit(self):
        eng = BehaviorEngine(loitering_seconds=100, shelf_exit_repeat_count=2, shelf_exit_time_window_seconds=60)
        pid = 3
        t0 = time.time()
        eng.update(pid, "shelf", now=t0)
        eng.update(pid, "exit", now=t0 + 5)
        eng.update(pid, "shelf", now=t0 + 10)
        triggers = eng.update(pid, "exit", now=t0 + 15)
        self.assertIn("Repeated Shelf–Exit Movement", triggers)

if __name__ == "__main__":
    unittest.main()
