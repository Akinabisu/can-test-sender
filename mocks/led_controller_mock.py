from led_controller import LEDMode
import asyncio

class LEDControllerMock:

    def __init__(self):
        self.led_mode = LEDMode.NORMAL

    def mode_to_hz(self) -> int:
        if (self.led_mode==LEDMode.NORMAL):
            return 1
        if (self.led_mode==LEDMode.FAST):
            return 4
        return 1

    async def blink(self):
        while (True):
            half_period = 1/self.mode_to_hz()/2
            print(f"ON for {half_period}s\n");
            await asyncio.sleep(half_period)
            print(f"OFF for {half_period}s\n");
            await asyncio.sleep(half_period)

    def set_mode(self, new_mode: LEDMode):
        self.led_mode = new_mode
        
    async def set_mode_for_period(self, new_mode: LEDMode, period: int = 1, end_mode: LEDMode = LEDMode.NORMAL):
        self.set_mode(new_mode)
        await asyncio.sleep(period)
        self.set_mode(end_mode)