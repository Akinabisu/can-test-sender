from led_controller import LEDMode
import asyncio

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
        
    async def setModeForPeriod(self, new_mode: LEDMode, period: int = 1, end_mode: LEDMode = LEDMode.NORMAL):
        self.setMode(new_mode)
        await asyncio.sleep(period)
        self.setMode(end_mode)