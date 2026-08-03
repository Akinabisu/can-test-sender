import asyncio
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class LEDMode(Enum):
    NORMAL = 1
    FAST = 4

    @property
    def frequency_hz(self) -> float:
        return float(self.value)

class LEDControllerMock:
    def __init__(self, gpio_pin: int):
        self.gpio_pin = gpio_pin
        self.led_mode = LEDMode.NORMAL
        self.is_on = False
        logger.info(f"[MOCK] Initialized mock LED on GPIO pin {gpio_pin}")

    async def blink(self):
        logger.info(f"[MOCK] Starting LED blinking loop on GPIO {self.gpio_pin}")
        try:
            while True:
                half_period = 1 / self.led_mode.frequency_hz / 2

                self.is_on = True
                logger.info(f"[MOCK] GPIO {self.gpio_pin} -> ON ({self.led_mode.name} mode)")
                await asyncio.sleep(half_period)

                self.is_on = False
                logger.info(f"[MOCK] GPIO {self.gpio_pin} -> OFF ({self.led_mode.name} mode)")
                await asyncio.sleep(half_period)

        except asyncio.CancelledError:
            logger.info(f"[MOCK] Blinking loop on GPIO {self.gpio_pin} canceled.")
            self.stop()
            raise
        except Exception as e:
            logger.error(f"[MOCK] Unexpected error in blinking loop: {e}")
            self.stop()
            raise

    def set_mode(self, new_mode: LEDMode):
        if self.led_mode != new_mode:
            logger.info(f"[MOCK] Changed mode on GPIO {self.gpio_pin}: {self.led_mode.name} -> {new_mode.name}")
            self.led_mode = new_mode

    async def set_mode_for_period(self, new_mode: LEDMode, period: float = 1.0, end_mode: LEDMode = LEDMode.NORMAL
    ):
        self.set_mode(new_mode)
        await asyncio.sleep(period)
        self.set_mode(end_mode)

    def stop(self):
        self.is_on = False
        logger.info(f"[MOCK] GPIO {self.gpio_pin} mock LED stopped.")