from enum import Enum

class LEDMode(Enum):
    NORMAL = 1
    FAST = 4

    @property
    def frequency(self) -> float:
        return float(self.value)