##########################################################################
#                             OBC Function 9                             #
#                              Event Logger                              #
##########################################################################
# Functions:
# - Log mode-change trigger events
# - Log payload events
# - Timestamp events

# event_logger.py
from datetime import datetime
import threading  # for background thread

class EventLogger:
    """    Logs and time-stamps mode changes and PL events    """

    def __init__(self, clock):
        self.clock = clock
        self.events: list[dict] = []   # store all event records
        self._lock = threading.Lock()  # for thread-safe access (avoids corruption from multiple simultaneous entries)

    def log_event(self, source: str, event_type: str, message: str):
        """
        Record new event with timestamp from onboard clock.
        """
        with self._lock:
            timestamp = self.clock.get_time()
            event = {
                "time": timestamp,
                "source": source,
                "type": event_type,
                "message": message
            }
            self.events.append(event)
            print(f"[EventLogger] {timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')} | {source} | {event_type} | {message}")

    def get_events(self):
        """
        Return all logged events.
        """
        with self._lock:
            return list(self.events)  # return a copy, so outside code can’t modify directly

    def get_recent_events(self, limit=5):
        """
        Return most recent 'limit' events.
        """
        with self._lock:
            return self.events[-limit:]

    def clear_log(self):
        """
        Clears all stored events.
        """
        with self._lock:
            self.events.clear()
            print("[EventLogger] Log cleared.")