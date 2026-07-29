from file_reader import FileReader
from encoder import Encoder
from buffer_editor import BufferEditor
from can_sender import CANSender
from i2c_scanner import I2CScanner
from led_controller import LEDControllerMock, LEDMode

import asyncio

READ_FILE_PATH = "input.txt"

async def emulateI2CScan(led_controller: LEDController):
    led_controller.setState(LEDMode.FAST)
    await asyncio.sleep(1)
    led_controller.setState(LEDMode.NORMAL)

async def main():
    content = FileReader.read(READ_FILE_PATH)
    edited_buffer = BufferEditor.editBuffer(content)
    encoded_data = Encoder.encode(edited_buffer)

    led_controller = LEDControllerMock()

    blink_task = asyncio.create_task(led_controller.blink())

    while True:
        await asyncio.sleep(4)
        await emulateI2CScan(led_controller)

if __name__ == "__main__":
    asyncio.run(main())