from enum import Enum

class LEDMode(Enum):
    NORMAL = 1
    FAST = 2


class LEDController:
    def blink(self):
        pass