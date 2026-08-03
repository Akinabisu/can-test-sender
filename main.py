import os
import asyncio
import logging
from pathlib import Path

USE_MOCKS = os.path.exists("/proc/device-tree/model")

if not USE_MOCKS:
    from mocks.i2c_scanner_mock import I2CScannerMock as I2CScanner
    from mocks.led_controller_mock import LEDControllerMock as LEDController, LEDMode
else:
    from i2c_scanner import I2CScanner
    from led_controller import LEDController, LEDMode

from file_reader import FileReader
from buffer_editor import BufferEditor
from can_sender import CANSender

logger = logging.getLogger(__name__)


RX_TXT = 0x700
TX_TXT = 0x701

RX_I2C = 0x702
TX_I2C = 0x703

SCAN_PERIOD = 60
LED_GPIO = 17

INPUT_PATH = Path(__file__).resolve().parent / "input.txt"

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s"
    )

async def periodic_i2c_scan_send_led(sender: CANSender, led_controller: LEDController, period: float):
    logger.info(f"Starting periodic I2C scan loop (interval: {period}s)")

    try:
        while True:
            await led_controller.set_mode_for_period(LEDMode.FAST, period=1.0)
            table_output = await asyncio.to_thread(I2CScanner.scan_to_str)
            await sender.send(RX_I2C, TX_I2C, table_output.encode("ascii", errors="replace"))
            await asyncio.sleep(period)

    except asyncio.CancelledError:
        logger.info("Periodic I2C scan task canceled")
        raise

async def main():
    setup_logging()
    
    content = FileReader.read(INPUT_PATH)
    edited_buffer = BufferEditor.edit_buffer(content)

    led_controller = LEDController(LED_GPIO)

    task_led = asyncio.create_task(led_controller.blink())

    async with CANSender() as sender:
        await sender.send(RX_TXT, TX_TXT, edited_buffer.encode("ascii", errors="replace"))

        task_i2c = asyncio.create_task(
            periodic_i2c_scan_send_led(sender, led_controller, SCAN_PERIOD)
        )

        logger.info("All services running. Press Ctrl+C to stop.")

        try:
            await asyncio.gather(task_led, task_i2c)

        except asyncio.CancelledError:
            logger.info("Canceling background tasks...")
            task_led.cancel()
            task_i2c.cancel()
            await asyncio.gather(task_led, task_i2c, return_exceptions=True)
            led_controller.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application terminated by user (Ctrl+C).")