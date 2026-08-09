import asyncio
import logging
from can_controller import CANController
from logger_setup import LoggerSetup

SENDER_RX_TXT = 0x700
SENDER_TX_TXT = 0x701

SENDER_RX_I2C = 0x702
SENDER_TX_I2C = 0x703

logger = logging.getLogger(__name__)

async def handle_message(controller: CANController, rx_id: int, tx_id: int) -> None:
    logger.info(f"Started receiving on (Rx: 0x{rx_id:03X}, Tx: 0x{tx_id:03X})")
    while True:
        await controller.receive(rx_id, tx_id)


async def main():
    LoggerSetup.setup_logging()

    async with CANController() as controller:
        task_txt = asyncio.create_task(handle_message(controller, SENDER_TX_TXT, SENDER_RX_TXT))

        task_i2c = asyncio.create_task(handle_message(controller, SENDER_TX_I2C, SENDER_RX_I2C))

        logger.info("All services running. Press Ctrl+C to stop.")

        try:
            await asyncio.gather(task_txt, task_i2c)
        except (asyncio.CancelledError, KeyboardInterrupt):
            logger.info("Canceling background tasks...")
            task_txt.cancel()
            task_i2c.cancel()
            await asyncio.gather(task_txt, task_i2c, return_exceptions=True)


if __name__ == "__main__":
    asyncio.run(main())