from file_reader import FileReader
from encoder import Encoder
from buffer_editor import BufferEditor
from can_sender import CANSender
from i2c_scanner import I2CScanner
from led_controller import LEDControllerMock, LEDMode

import asyncio

READ_FILE_PATH = "input.txt"

RX_TXT = 0x700
TX_TXT = 0x701

RX_I2C = 0x702
TX_I2C = 0x703

SEND_PERIOD = 60

async def periodic_mode_changer(led_controller: LEDControllerMock):
    while True:
            await asyncio.sleep(4)
            led_controller.setMode(LEDMode.FAST)
            await asyncio.sleep(1)
            led_controller.setMode(LEDMode.NORMAL)

async def main():
    content = FileReader.read(READ_FILE_PATH)
    edited_buffer = BufferEditor.editBuffer(content)
    encoded_data = Encoder.encode(edited_buffer)

    led_controller = LEDControllerMock()

    task_led = asyncio.create_task(led_controller.blink())
    task_led_mode = asyncio.create_task(periodic_mode_changer(led_controller))

    async with CANSender() as sender:
        await sender.send(RX_TXT, TX_TXT, encoded_data)
        task_i2c = asyncio.create_task(sender.sendPeriodically(RX_I2C, TX_I2C, Encoder.encode("Hello"), SEND_PERIOD))    

if __name__ == "__main__":
    asyncio.run(main())