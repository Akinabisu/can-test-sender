import asyncio
import logging
from enum import Enum
from gpiozero import LED

logger = logging.getLogger(__name__)

class LEDMode(Enum):
    NORMAL = 1
    FAST = 4

    @property
    def frequency_hz(self) -> float:
        return float(self.value)

class LEDController:
    def __init__(self, gpio_pin: int):
        self.gpio_pin = gpio_pin
        self.led_mode = LEDMode.NORMAL
        self.led = LED(gpio_pin)
        logger.info(f"Initialized LEDController on GPIO pin {gpio_pin}")

    async def blink(self):
        logger.info(f"Starting LED blinking loop on GPIO {self.gpio_pin}")
        try:
            while True:
                half_period = 1 / self.led_mode.frequency_hz / 2
                
                self.led.on()
                await asyncio.sleep(half_period)
                self.led.off()
                await asyncio.sleep(half_period)

        except asyncio.CancelledError:
            logger.info(f"LED blinking loop on GPIO {self.gpio_pin} canceled. Cleaning up...")
            self.stop()
            raise
        except Exception as e:
            logger.error(f"Unexpected error in LED blinking loop: {e}")
            self.stop()
            raise

    def set_mode(self, new_mode: LEDMode):
        if self.led_mode != new_mode:
            logger.info(f"Changed LED mode from {self.led_mode.name} to {new_mode.name}")
            self.led_mode = new_mode

    async def set_mode_for_period(self, new_mode: LEDMode, period: float = 1.0, end_mode: LEDMode = LEDMode.NORMAL
    ):
        self.set_mode(new_mode)
        await asyncio.sleep(period)
        self.set_mode(end_mode)

    def stop(self):
        self.led.off()
        self.led.close()
        logger.info(f"LED on GPIO {self.gpio_pin} stopped and hardware closed.")