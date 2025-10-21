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


class ModeManager:
    """Very simple mode manager with free switching between modes."""
    def __init__(self):
        self.mode = "STANDBY"

    def set_mode(self, new_mode: str):
        old_mode = self.mode
        self.mode = new_mode.upper()
        print(f"[MODE CHANGE] {old_mode} → {self.mode}")

    def get_mode(self) -> str:
        return self.mode