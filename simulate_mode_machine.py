# simulate_threaded_verbose.py
import threading
import time
import numpy as np
import random
import os
from housekeeping import ModeMachine, battery_level, spinning_ratio, temperature, State



def background_loop(mm: ModeMachine, stop_event: threading.Event, lock: threading.Lock, interval: float = 5.0):
    step = 0
    while not stop_event.is_set():
        step += 1
        # take measurements
        batt = battery_level()
        spin = spinning_ratio()
        temp = temperature()

        # apply updates under lock to avoid races with telecommand thread
        with lock:
            state_before = mm.get_state()
            mm.battery_update(batt)
            mm.attitude_rate_update(spin)
            state_after = mm.get_state()

        # timestamp
        ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        # Print a clear line for this sample
        if state_before is state_after:
            print(f"[{ts}] STEP {step:05d} | state={state_after.name:10s} | batt={batt:6.2f}% | spin={spin:6.1f}°/s | temp={temp:6.1f}°C")
        else:
            # highlight transition
            print(f"[{ts}] STEP {step:05d} | {state_before.name} -> {state_after.name}  | batt={batt:6.2f}% | spin={spin:6.1f}°/s | temp={temp:6.1f}°C")
            # on_state_change callback will also print a state-change line (if configured)

        # Wait up to `interval` seconds, but break early if stop_event is set
        if stop_event.wait(interval):
            break

    print("Background loop exiting.")


def main():
    #print("Interactive threaded simulator (type 'help' for commands).")
    lock = threading.Lock()
    stop_event = threading.Event()

    # Callback for state changes from ModeMachine (keeps user informed instantly)
    def on_state_change(old, new):
        print(f" STATE CHANGE: {old.name} → {new.name}")

    mm = ModeMachine(on_state_change=on_state_change)
   
    mm.antenna_deployed(success=False)
    time.sleep(5)
    mm.antenna_deployed(success=True)  # move out of STARTUP into DETUMBLING initially

    # Start background thread (5 second interval)
    bg_thread = threading.Thread(target=background_loop, args=(mm, stop_event, lock, 5.0), daemon=True)
    bg_thread.start()

    # Main thread: accept interactive commands
    try:
        while True:
            cmd = input("cmd> ").strip().lower()
            if not cmd:
                continue

            if cmd in ("quit", "exit", "stop_sim"):
                print("Stopping simulator...")
                stop_event.set()
                break

            if cmd == "help":
                print("Commands:")
                print("  science    - telecommand to start science (from STANDBY)")
                print("  downlink   - start downlink (from STANDBY)")
                print("  stop       - stop downlink/science and go to STANDBY")
                print("  standby    - force STANDBY")
                print("  safemode   - force SAFEMODE (if allowed by telecommand handler)")
                print("  detumbling - force DETUMBLING")
                print("  status     - print current state")
                print("  quit/exit/stop_sim - stop simulation and exit")
                continue

            if cmd == "status":
                with lock:
                    s = mm.get_state()
                print(f"Current state: {s.name}")
                continue

            # send telecommand (protected by lock)
            with lock:
                mm.telecommand(cmd)

            # small pause so the background loop can show any immediate transitions if they happen
            time.sleep(0.05)

    except (KeyboardInterrupt, EOFError):
        
        stop_event.set()

    # wait for background to finish
    bg_thread.join()
    print("Simulator stopped.")

if __name__ == "__main__":
    main()
