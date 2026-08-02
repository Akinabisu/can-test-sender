import asyncio
from enum import Enum
from gpiozero import LED

class LEDMode(Enum):
    NORMAL = 1
    FAST = 2

class LEDController:
    
    def __init__(self, gpio_pin: int):
        self.led_mode = LEDMode.NORMAL
        self.led = LED(gpio_pin)

    def mode_to_hz(self) -> int:
        if (self.led_mode==LEDMode.NORMAL):
            return 1
        if (self.led_mode==LEDMode.FAST):
            return 4
        return 1

    async def blink(self):
        print("LED blinking")
        while (True):
            half_period = 1/self.mode_to_hz()/2
            self.led.on()
            await asyncio.sleep(half_period)
            self.led.off()
            await asyncio.sleep(half_period)

    def set_mode(self, new_mode: LEDMode):
        print(f"LED set mode to {new_mode}")
        self.led_mode = new_mode

    async def set_mode_for_period(self, new_mode: LEDMode, period: int = 1, end_mode: LEDMode = LEDMode.NORMAL):
        self.set_mode(new_mode)
        await asyncio.sleep(period)
        self.set_mode(end_mode)