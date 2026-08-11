import asyncio
import logging
import os
import isotp

logger = logging.getLogger(__name__)

MAX_REGULAR_ID = 0x7FF
MAX_EXTENDED_ID = 0x1FFFFFFF

class CANController:
    def __init__(self, channel: str = os.getenv("CAN_CHANNEL", "vcan0")):
        self.channel = channel
        self.connections: dict[tuple[int, int], isotp.socket] = {}
        logger.info(f"Initialized CAN Controller on '{self.channel}'")

    def _get_or_create_socket(self, rx_id: int, tx_id: int) -> isotp.socket:
        if not isinstance(rx_id, int) or not (0 <= rx_id <= MAX_EXTENDED_ID):
            logger.error(f"Invalid Rx ID 0x{rx_id:X} for ISO-TP address")
            raise ValueError(f"Rx ID 0x{rx_id:X} out of bounds  (0x0 - 0x{MAX_EXTENDED_ID:X})")

        if not isinstance(tx_id, int) or not (0 <= tx_id <= MAX_EXTENDED_ID):
            logger.error(f"Invalid Tx ID 0x{tx_id:X} for ISO-TP address")
            raise ValueError(f"Tx ID 0x{tx_id:X} out of bounds (0x0 - 0x{MAX_EXTENDED_ID:X})")
        
        key = (rx_id, tx_id)
        is_extended = rx_id > MAX_REGULAR_ID or tx_id > MAX_REGULAR_ID

        if key not in self.connections:
            sock = isotp.socket()

            if is_extended:
                address = isotp.Address(
                    rxid=rx_id, txid=tx_id, flags=isotp.AddressFlags.CAN_ID_EXTENDED
                )
            else:
                address = isotp.Address(
                    rxid=rx_id, txid=tx_id
                )

            sock.bind(self.channel, address=address)
            self.connections[key] = sock

            logger.info(f"Created ISO-TP socket on '{self.channel}' (Tx: 0x{tx_id:X}, Rx: 0x{rx_id:X})")
        else:
            logger.info(f"Reusing existing ISO-TP socket on '{self.channel}' (Tx: 0x{tx_id:X}, Rx: 0x{rx_id:X})")

        return self.connections[key]

    async def send(self, rx_id: int, tx_id: int, data: bytes) -> None:
        key = (rx_id, tx_id)
        sock = self._get_or_create_socket(rx_id, tx_id)

        try:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, sock.send, data)
        except Exception:
            logger.exception(f"Error sending CAN data on Tx: 0x{tx_id:X} -> Rx: 0x{rx_id:X}")
            self._close_single_socket(key)
            raise

        logger.info(f"Sent message on {self.channel} Tx: 0x{tx_id:X} -> Rx: 0x{rx_id:X} | {len(data)} bytes: {data}")

    async def receive(self, rx_id: int, tx_id: int) -> bytes:
        key = (rx_id, tx_id)
        sock = self._get_or_create_socket(rx_id, tx_id)

        try:
            loop = asyncio.get_running_loop()
            data = await loop.run_in_executor(None, sock.recv)
        except Exception:
            logger.exception(f"Error receiving CAN data on Rx: 0x{rx_id:X} -> Tx: 0x{tx_id:X}")
            self._close_single_socket(key)
            raise

        logger.info(f"Received message on {self.channel} Rx: 0x{rx_id:X} <- Tx: 0x{tx_id:X} | {len(data)} bytes: {data}")
        return data
    
    def _close_single_socket(self, key: tuple[int, int]) -> None:
        if key in self.connections:
            sock = self.connections.pop(key)
            try:
                sock.close()
                logger.info(f"Closed ISO-TP socket for Tx: 0x{key[1]:X}, Rx: 0x{key[0]:X}")
            except Exception:
                logger.exception(f"Error closing ISO-TP socket for Tx: 0x{key[1]:X}, Rx: 0x{key[0]:X}")

    def close(self) -> None:
        logger.info(f"Closing all ISO-TP sockets on '{self.channel}'")
        for key in list(self.connections.keys()):
            self._close_single_socket(key)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.close()