import asyncio
import logging
import os
import isotp

logger = logging.getLogger(__name__)

class CANSender:
    def __init__(self, rx_id: int, tx_id: int, channel: str | None = None):
        if not isinstance(rx_id, int) or rx_id < 0:
            logger.error(f"Invalid rx_id '{rx_id}'. Must be a non-negative integer.")
            raise ValueError("rx_id must be a non-negative integer")
        if not isinstance(tx_id, int) or tx_id < 0:
            logger.error(f"Invalid tx_id '{tx_id}'. Must be a non-negative integer.")
            raise ValueError("tx_id must be a non-negative integer")

        self.channel = channel or os.getenv("CAN_CHANNEL", "vcan0")
        self.rx_id = rx_id
        self.tx_id = tx_id
        self.sock: isotp.socket | None = None

    async def _connect(self):
        if self.sock is not None:
            return

        logger.info(
            f"Binding ISO-TP socket on '{self.channel}' "
            f"(Tx: 0x{self.tx_id:03X}, Rx: 0x{self.rx_id:03X})..."
        )
        try:
            addr = isotp.Address(rxid=self.rx_id, txid=self.tx_id)
            self.sock = await asyncio.to_thread(isotp.socket)
            await asyncio.to_thread(self.sock.bind, self.channel, address=addr)
        except OSError as e:
            logger.error(
                f"Failed to bind ISO-TP socket on '{self.channel}' "
                f"(Tx: 0x{self.tx_id:03X}, Rx: 0x{self.rx_id:03X}): {e}"
            )
            await self.close()
            raise

    async def send(self, data: bytes):
        if self.sock is None:
            await self._connect()

        try:
            await asyncio.to_thread(self.sock.send, data)
            logger.info(
                f"Sent {len(data)} bytes on {self.channel} "
                f"Tx: 0x{self.tx_id:03X} -> Rx: 0x{self.rx_id:03X}"
            )
        except (OSError, isotp.IsoTpError) as e:
            logger.error(f"Failed to send CAN data: {e}")
            raise

    async def send_periodically(self, data: bytes, period: float):
        logger.info(
            f"Starting periodic transmission on '{self.channel}' "
            f"(Tx: 0x{self.tx_id:03X}, Rx: 0x{self.rx_id:03X}, period: {period}s)"
        )
        try:
            while True:
                await self.send(data)
                await asyncio.sleep(period)
        except asyncio.CancelledError:
            logger.info(
                f"Periodic CAN transmission task (Tx: 0x{self.tx_id:03X}, Rx: 0x{self.rx_id:03X}) canceled."
            )
            raise

    async def close(self):
        if self.sock is not None:
            logger.info(f"Closing active CAN connection on '{self.channel}'...")
            try:
                sock, self.sock = self.sock, None
                await asyncio.to_thread(sock.close)
            except Exception as e:
                logger.debug(f"Error closing socket: {e}")

    async def __aenter__(self):
        await self._connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()