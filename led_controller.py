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

    def ModeToHz(self) -> int:
        if (self.led_mode==LEDMode.NORMAL):
            return 1
        if (self.led_mode==LEDMode.FAST):
            return 4
        return 1

    async def blink(self):
        while (True):
            half_period = 1/self.ModeToHz()/2
            self.led.on()
            await asyncio.sleep(half_period)
            self.led.off()
            await asyncio.sleep(half_period)

    def setMode(self, new_mode: LEDMode):
        self.led_mode = new_mode

class LEDControllerMock:

    def __init__(self):
        self.led_mode = LEDMode.NORMAL

    def ModeToHz(self) -> int:
        if (self.led_mode==LEDMode.NORMAL):
            return 1
        if (self.led_mode==LEDMode.FAST):
            return 4
        return 1

    async def blink(self):
        while (True):
            half_period = 1/self.ModeToHz()/2
            print(f"ON for {half_period}s\n");
            await asyncio.sleep(half_period)
            print(f"OFF for {half_period}s\n");
            await asyncio.sleep(half_period)

    def setMode(self, new_mode: LEDMode):
        self.led_mode = new_mode