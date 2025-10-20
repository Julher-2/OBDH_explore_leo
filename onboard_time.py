##########################################################################
#                             OBC Function 7                             #
#                              Onboard Time                              #
##########################################################################
# Functions:
# - Check and show "onboard time" via TM
# - Change "onboard time" via TC

from datetime import datetime, timedelta, timezone
import time  # for sleep
import threading  # for background thread

class OnboardTime:
    """    Simple onboard clock    """

    def __init__(self,tick_interval=1):
        # __init__ automatically initializes new object’s attributes and initial state
        # Start with current system UTC time
        self.current_time = datetime.now(timezone.utc)
        self.tick_interval = tick_interval  # seconds (=1 assumed)
        self._running = False               # flag for background thread
        self._lock = threading.Lock()       # for thread-safe access (avoids corruption from multiple simultaneous entries)

    def get_time(self):
        """
        Return current onboard time.
        """
        with self._lock:
            return self.current_time

    def set_time(self, new_time_str):
        """
        Change onboard time via TC (ISO format string).
        """
        try:
            # Convert the string to a datetime object.
            # Must also accept "Z" format (CCSDS and ECSS standard)
            new_time = datetime.fromisoformat(new_time_str.replace("Z", "+00:00"))
            with self._lock:
                self.current_time = new_time
            print(f"[OBC] Onboard time successfully updated to {self.current_time.strftime('%Y-%m-%dT%H:%M:%SZ')}")
            return True
        except ValueError as e:
            print(f"[OBC] Invalid time format: {e}. Use ISO format, e.g. 2025-10-20T12:30:00Z")
            return False

    def tick(self, seconds=1):
        """
        Advance onboard time by 'seconds' (simulate clock ticking).
        """
        with self._lock:
            self.current_time += timedelta(seconds=seconds)

    def start_clock(self):
        """
        Start background thread to automatically advance the clock every tick_interval seconds.
        """
        if not self._running:
            self._running = True
            thread = threading.Thread(target=self._run_clock, daemon=True)
            thread.start()

    def stop_clock(self):
        """
        Stop the background clock.
        """
        self._running = False

    def _run_clock(self):
        """
        Internal method run in a background thread.
        """
        while self._running:
            time.sleep(self.tick_interval)
            self.tick(self.tick_interval)