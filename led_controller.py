import asyncio
import logging
from gpiozero import LED
from led_mode import LEDMode

logger = logging.getLogger(__name__)

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
                half_period = 1 / self.led_mode.frequency / 2
                
                self.led.on()
                await asyncio.sleep(half_period)
                self.led.off()
                await asyncio.sleep(half_period)

        except asyncio.CancelledError:
            logger.info(f"LED blinking loop on GPIO {self.gpio_pin} canceled")
            self.stop()
            raise
        except Exception as e:
            logger.exception(f"Unexpected error in LED blinking loop on GPIO {self.gpio_pin}")
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
        try:
            self.led.off()
            self.led.close()
            logger.info(f"LED on GPIO {self.gpio_pin} stopped and hardware closed.")
        except Exception:
            logger.exception(f"Error while stopping LED on GPIO {self.gpio_pin}")