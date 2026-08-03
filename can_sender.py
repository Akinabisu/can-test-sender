import asyncio
import logging
import can
import isotp
import os

logger = logging.getLogger(__name__)

class CANSender:
    def __init__(
        self, 
        channel: str = os.getenv("CAN_CHANNEL", "vcan0"), 
        interface: str = os.getenv("CAN_INTERFACE", "socketcan"), 
    ):
        self.channel = channel
        self.interface = interface
        self.bus = can.interface.Bus(channel=self.channel, bustype=self.interface)
        self.connections: dict[tuple[int, int], isotp.CanStack] = {}
        self.connections: dict[tuple[int, int], isotp.CanStack] = {}
        logger.info(f"Initialized CANSender on '{self.channel}' ({self.interface})")

    def _get_or_create_stack(self, rx_id: int, tx_id: int) -> isotp.CanStack:
        key = (rx_id, tx_id)

        if key not in self.connections:
            logger.info(f"Creating ISO-TP stack on '{self.channel}' (Tx: 0x{tx_id:03X}, Rx: 0x{rx_id:03X})...")
            try:
                address = isotp.Address(
                    rxid=rx_id,
                    txid=tx_id
                )
                stack = isotp.CanStack(
                    bus=self.bus,
                    address=address,
                    params={
                        'stmin': 0,
                        'blocksize': 0,
                        'tx_data_length': 8
                    }
                )
                self.connections[key] = stack

            except Exception as e:
                logger.error(
                    f"Failed to create ISO-TP stack on '{self.channel}' "
                    f"(Tx: 0x{tx_id:03X}, Rx: 0x{rx_id:03X}): {e}"
                )
                raise

        return self.connections[key]

    async def send(self, rx_id: int, tx_id: int, data: bytes):
        key = (rx_id, tx_id)

        try:
            stack = self._get_or_create_stack(rx_id, tx_id)

            stack.send(data)

            while stack.transmitting():
                stack.process()
                await asyncio.sleep(0.001)

            logger.info(f"Sent message on {self.channel} Tx: 0x{tx_id:03X} -> Rx: 0x{rx_id:03X} | {len(data)} bytes: {data.hex()}")

        except Exception as e:
            logger.error(f"Error sending CAN data on Tx 0x{tx_id:03X}: {e}")
            self._close_single_socket(key)
            raise

    async def send_periodically(self, rx_id: int, tx_id: int, data: bytes, period: float):
        logger.info(
            f"Starting periodic transmission on '{self.channel}' "
            f"(Tx: 0x{tx_id:03X}, Rx: 0x{rx_id:03X}, period: {period}s)"
        )
        try:
            while True:
                await self.send(rx_id, tx_id, data)
                await asyncio.sleep(period)

        except asyncio.CancelledError:
            logger.info(
                f"Periodic CAN transmission task (Tx: 0x{tx_id:03X}, Rx: 0x{rx_id:03X}) canceled."
            )
            raise

    def _close_single_socket(self, key: tuple[int, int]):
        stack = self.connections.pop(key, None)
        if stack:
            pass

    def close(self):
        logger.info(f"Closing all open CAN connections on '{self.channel}'...")
        self.connections.clear()
        
        if hasattr(self, 'bus') and self.bus:
            try:
                self.bus.shutdown()
            except Exception as e:
                logger.debug(f"Error closing CAN bus: {e}")

        logger.info("CANSender shutdown complete.")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.close()