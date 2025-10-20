##########################################################################
#                             OBC Function 8                             #
#                               Scheduler                                #
##########################################################################
# Functions:
# - Send timetagged TC
# - Confirm execution on time
# - Reject if time exceeded

# scheduler.py
import time  # for sleep
import threading  # for background ticking
import heapq  # for queuing commands
from datetime import datetime

class Scheduler:
    """    Handles timetagged telecommands (TC)    """

    def __init__(self, clock):
        self.clock = clock              # link to OnboardTime for current time
        self.tc_queue: list[dict] = []  # list of scheduled commands, format {"time": datetime, "command": str, "executed": bool}
        self._running = False           # flag for background thread
        self._lock = threading.Lock()   # for thread-safe access (avoids corruption from multiple simultaneous entries)

    def schedule_tc(self, command, execute_time_str):
        """
        Schedule new TC at specific onboard time (ISO format string).
        """
        try:
            execute_time = datetime.fromisoformat(execute_time_str.replace("Z", "+00:00"))
            with self._lock:
                self.tc_queue.append({
                    "time": execute_time,
                    "command": command,
                    "executed": False
                })
                self.tc_queue.sort(key=lambda tc: tc["time"])
            print(f"[Scheduler] TC '{command}' scheduled for {execute_time_str}")
            return True
        except ValueError as e:
            print(f"[Scheduler] Invalid time format: {e}. Use ISO format, e.g. 2025-10-20T12:30:00Z")
            return False
    
    def check_and_execute(self):
        """
        Check all scheduled commands and execute those whose time has arrived.
        """
        current_time = self.clock.get_time()
        with self._lock:
            # While commands exist in queue and the next scheduled is due
            while self.tc_queue and current_time >= self.tc_queue[0]["time"]:
                tc = self.tc_queue.pop(0)
                command = tc["command"]
                tc["executed"] = True
                print(
                f"[Scheduler] Executing TC '{command}' "
                f"(scheduled for {tc['time'].strftime('%Y-%m-%dT%H:%M:%SZ')}) "
                f"at {current_time.strftime('%Y-%m-%dT%H:%M:%SZ')}"
                )
                # Here you could actually trigger the payload or log the event
            
    def start_tc_check(self, interval=1):
        """
        Start background thread to check scheduled commands every 'interval' seconds.
        """
        self._running = True
        thread = threading.Thread(target=self._run_tc_check, args=(interval,), daemon=True)
        thread.start()

    def stop_tc_check(self):
        self._running = False

    def _run_tc_check(self, interval):
        while self._running:
            self.check_and_execute()
            time.sleep(interval)