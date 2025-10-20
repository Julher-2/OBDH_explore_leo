##########################################################################
#                                OBC main                                #
##########################################################################
# Structure:
# SpacecraftSim.sln
# ├── MCS/
# │   ├── mcs.py
# │   └── mcs_functions/
# │       ├── 
# │       ├── 
# │       └── 
# ├── OBC/
# │   ├── obc.py
# │   └── obc_functions/
# │       ├── onboard_time.py
# │       ├── scheduler.py
# │       └── event_logger.py
# └── ICU/
#     ├── icu.py
#     └── icu_functions/
#         ├── 
#         ├── 
#         └── 
#-------------------------------------------------------------------------

import time
from datetime import timedelta
# import functions
from scheduler import Scheduler
from onboard_time import OnboardTime
from event_logger import EventLogger


# ---------- OnboardTime -------------------------------------------------

# Start onboard clock
clock = OnboardTime(tick_interval=1)
clock.start_clock()

# Show time every 1 seconds
for _ in range(5):
    print(f"Current onboard time: {clock.get_time().strftime('%Y-%m-%dT%H:%M:%SZ')}")
    time.sleep(1)

# Change onboard time via TC
new_time = "2025-10-19T12:00:00Z"
clock.set_time(new_time)

# ---------- Scheduler ---------------------------------------------------

# Create scheduler linked to clock
sched = Scheduler(clock)
sched.start_tc_check(interval=1)  # run background checking

# Schedule a TC 5 seconds in the future
future_time = (clock.get_time() + timedelta(seconds=5)).strftime("%Y-%m-%dT%H:%M:%SZ")
sched.schedule_tc("TAKE_PICTURE", future_time)

# Wait 10 seconds to see execution
time.sleep(10)
sched.stop_tc_check()

# ---------- EventLogger -------------------------------------------------

# Create logger linked to clock
logger = EventLogger(clock)

logger.log_event("OBC", "MODE_CHANGE", "Switched to SAFE mode")
time.sleep(2)
logger.log_event("Payload", "PAYLOAD_EVENT", "Image capture started")
time.sleep(1)
logger.log_event("Payload", "PAYLOAD_EVENT", "Image capture complete")

print("\nAll events:")
for event in logger.get_events():
    print(event)

# ---------- OnboardTime -------------------------------------------------

# Stop the background clock
clock.stop_clock()