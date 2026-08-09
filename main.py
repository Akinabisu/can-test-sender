import os
import asyncio
import logging
from pathlib import Path

IS_RASPBERRY_PI = os.path.exists("/proc/device-tree/model")

if IS_RASPBERRY_PI:
    from i2c_scanner import I2CScanner
    from led_controller import LEDController, LEDMode
else:
    from mocks.i2c_scanner_mock import I2CScannerMock as I2CScanner
    from mocks.led_controller_mock import LEDControllerMock as LEDController, LEDMode

from can_controller import CANController
from file_reader import FileReader
from buffer_editor import BufferEditor
from can_controller import CANController
from logger_setup import LoggerSetup

logger = logging.getLogger(__name__)

SENDER_RX_TXT = 0x700
SENDER_TX_TXT = 0x701

SENDER_RX_I2C = 0x702
SENDER_TX_I2C = 0x703

SCAN_PERIOD = 60.0
LED_GPIO = 17

INPUT_PATH = Path(__file__).resolve().parent / "input.txt"

async def periodic_i2c_scan_send_led(controller: CANController, led_controller: LEDController, period: float):
    logger.info(f"Starting periodic I2C scan loop (interval: {period}s)")

    try:
        while True:
            await led_controller.set_mode_for_period(LEDMode.FAST, period=1.0)
            table_output = await asyncio.to_thread(I2CScanner.scan_to_str)
            await controller.send(SENDER_RX_I2C, SENDER_TX_I2C, table_output.encode("ascii", errors="replace"))
            await asyncio.sleep(period)

    except asyncio.CancelledError:
        logger.info("Periodic I2C scan task canceled")
        raise

async def main():
    LoggerSetup.setup_logging()
    
    content = await asyncio.to_thread(FileReader.read, INPUT_PATH)
    edited_buffer = BufferEditor.edit_buffer(content)

    led_controller = LEDController(LED_GPIO)


    async with CANController() as controller:
        task_led = asyncio.create_task(led_controller.blink())

        await controller.send(SENDER_RX_TXT, SENDER_TX_TXT, edited_buffer.encode("ascii", errors="replace"))

        task_i2c = asyncio.create_task(
            periodic_i2c_scan_send_led(controller, led_controller, SCAN_PERIOD)
        )

        logger.info("All services running. Press Ctrl+C to stop.")
        try:
            await asyncio.gather(task_led, task_i2c)

        except (asyncio.CancelledError, KeyboardInterrupt):
            logger.info("Canceling background tasks...")
            task_led.cancel()
            task_i2c.cancel()
            await asyncio.gather(task_led, task_i2c, return_exceptions=True)

if __name__ == "__main__":
    asyncio.run(main())