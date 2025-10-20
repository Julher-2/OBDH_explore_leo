import random
from enum import Enum, auto
from typing import Callable, Optional


def battery_level():
    if random.random() < 0.95:  # 80% chance
        value = random.uniform(30, 100)  # between 30 and 100
    else:
        value = random.uniform(0, 30)    # between 0 and 30

    return round(value, 2)  # round to two decimal places


def spinning_ratio():
    if random.random() < 0.9:  # 90% chance
        value = random.uniform(0,5 )  # between 0 and 10
    else:
        value = random.uniform(5, 360)    # between 0 and 30

    return round(value, 1)  # round to two decimal places

def temperature():
    if random.random()<0.7:
        value=random.uniform(0,50)
    else:
        value = random.uniform(50,300)
    return round(value, 1)



class State(Enum):
    STARTUP = auto()
    DETUMBLING = auto()
    SAFEMODE = auto()
    STANDBY = auto()
    DOWNLINK = auto()
    SCIENCE = auto()


class ModeMachine:
    def __init__(
        self,
        hard_limit_attitude: float = 8.0,
        soft_limit_attitude: float = 5.0,
        hard_limit_battery: float = 30.0,
        soft_limit_battery: float = 40.0,
        temperature_limit: float = 55.0,
        on_state_change: Optional[Callable[[State, State], None]] = None,
    ):
        """
        safe_limit: attitude change rate below which detumbling -> safemode (very slow)
        soft_limit: attitude change rate above which standby -> detumbling (too fast)
        min_battery: battery percent below which standby -> safemode
        on_state_change: optional callback(old_state, new_state)
        """
        self.state = State.STARTUP
        self.hard_limit_attitude = hard_limit_attitude
        self.soft_limit_attitude = soft_limit_attitude
        self.hard_limit_battery = hard_limit_battery
        self.soft_limit_battery = soft_limit_battery
        self.temperature_limit = temperature_limit
        self.on_state_change = on_state_change or (lambda old, new: None)

    def _change_state(self, new_state: State):
        old = self.state
        if old is new_state:
            return
        self.state = new_state
        self.on_state_change(old, new_state)

    # Events / Commands
    def antenna_deployed(self, success: bool):
        """Called during startup when antenna and panels attempted deploy."""
        if self.state != State.STARTUP:
            return
        if success:
            self._change_state(State.DETUMBLING)
            print(f"ANTENNA DEPLOYED.")
        else:
            print(f"ANTENNA COULD NOT DEPLOY. STAY IN STARTUP MODE.")
            # loop in startup (no change), optionally will retry externally
            pass

    def attitude_rate_update(self, spinning_ratio):
        """
        Call whenever attitude change rate measurement arrives.
        rate: (e.g.) degrees/sec or rad/sec — thresholds are unit-consistent.
        """
        if self.state == State.DETUMBLING:
            # If the attitude rate is very low (below safe_limit) -> SAFEMODE
            if spinning_ratio > self.hard_limit_attitude:
                self._change_state(State.SAFEMODE)
            if spinning_ratio < self.soft_limit_attitude:
                self._change_state(State.STANDBY)

        elif self.state == State.STANDBY:
            # If attitude rate above soft_limit (too fast) -> DETUMBLING
            if spinning_ratio > self.soft_limit_attitude:
                self._change_state(State.DETUMBLING)
        elif self.state == State.SCIENCE:
            # If attitude rate above soft_limit (too fast) -> DETUMBLING
            if spinning_ratio > self.soft_limit_attitude:
                self._change_state(State.DETUMBLING)

        # Other states: we ignore attitude-rate-based transitions here

    def battery_update(self, battery_level):
        """
        Battery monitoring. If below min_battery while in STANDBY -> SAFEMODE.
        (You could generalize to other states if required.)
        """
        if (self.state == State.SCIENCE or self.state ==State.DETUMBLING) and battery_level < self.soft_limit_battery:
            self._change_state(State.STANDBY)
        if self.state == State.STANDBY and battery_level < self.hard_limit_battery:
            self._change_state(State.SAFEMODE)
     
    def telecommand(self, cmd: str):
        """
        Handle telecommands.
        Added debug prints and a testing 'force_science' command.
        """
        cmd = cmd.lower().strip()
        # debug line: show the incoming command and current state
        print(f"[telecommand] received='{cmd}' current_state={self.state.name}")

        if self.state == State.SAFEMODE:
            if cmd == "standby":
                self._change_state(State.STANDBY)
            # else ignore

        elif self.state == State.STANDBY:
            if cmd == "downlink":
                self._change_state(State.DOWNLINK)
            elif cmd == "science":
                self._change_state(State.SCIENCE)
            elif cmd == "detumbling":
                self._change_state(State.DETUMBLING)

        elif self.state in (State.DOWNLINK, State.SCIENCE):
            if cmd in ("stop", "standby"):
                self._change_state(State.STANDBY)

        elif self.state == State.DETUMBLING:
            if cmd == "safemode":
                self._change_state(State.SAFEMODE)
            elif cmd == "standby":
                self._change_state(State.STANDBY)

        elif self.state == State.STARTUP:
            if cmd == "force_startup_retry":
                pass

        # TESTING helpers (force commands) - always handled regardless of state
        if cmd == "force_science":
            print("[telecommand] force_science -> forcing SCIENCE")
            self._change_state(State.SCIENCE)
        if cmd == "force_standby":
            print("[telecommand] force_standby -> forcing STANDBY")
            self._change_state(State.STANDBY)

    # helper for external queries
    def get_state(self) -> State:
        return self.state



