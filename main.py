import os
import sys

if not os.path.exists("/proc/device-tree/model"):
    os.environ["GPIOZERO_PIN_FACTORY"] = "mock"
    from gpiozero.pins.mock import MockFactory

from file_reader import FileReader
from encoder import Encoder
from buffer_editor import BufferEditor
from can_sender import CANSender
from i2c_scanner import I2CScanner

from led_controller import LEDController, LEDMode

import asyncio

READ_FILE_PATH = "input.txt"

RX_TXT = 0x700
TX_TXT = 0x701

RX_I2C = 0x702
TX_I2C = 0x703

SCAN_PERIOD = 60

LED_GPIO = 17

async def periodicI2CScanSendLED(sender: CANSender, led_controller: LEDController, period: int):
    while (True):
        asyncio.create_task(led_controller.setModeForPeriod(LEDMode.FAST))
        scan_result = await asyncio.to_thread(I2CScanner.scan)
        print(scan_result)
        encoded_scan_result = Encoder.encode(scan_result)
        await sender.send(RX_I2C, TX_I2C, encoded_scan_result)
        await asyncio.sleep(period)

async def main():
    content = FileReader.read(READ_FILE_PATH)
    edited_buffer = BufferEditor.editBuffer(content)
    encoded_data = Encoder.encode(edited_buffer)

    led_controller = LEDController(LED_GPIO)
    task_led = asyncio.create_task(led_controller.blink())

    async with CANSender() as sender:
        task_txt = asyncio.create_task(sender.send(RX_TXT, TX_TXT, encoded_data))
        task_i2c = asyncio.create_task(periodicI2CScanSendLED(sender, led_controller, SCAN_PERIOD))

        await asyncio.gather(task_led, task_txt, task_i2c)

if __name__ == "__main__":
    asyncio.run(main())