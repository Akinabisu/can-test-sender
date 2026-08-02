import asyncio
import isotp


class CANSender:
    def __init__(self, channel: str = "vcan0"):
        self.channel = channel
        self.connections = {}

    async def send(self, rx_id: int, tx_id: int, data: bytes):
        key = (rx_id, tx_id)

        if key not in self.connections:
            sock = isotp.socket()

            addr = isotp.Address(
                rxid=rx_id,
                txid=tx_id
            )

            sock.bind(self.channel, address=addr)
            self.connections[key] = sock

        sock = self.connections[key]

        try:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, sock.send, data)
            print(f"SENT: {data}")

        except Exception as e:
            print(f"Failed to send CAN data: {e}")


    async def send_periodically(
        self,
        rx_id: int,
        tx_id: int,
        data: bytes,
        period: float
    ):
        while True:
            await self.send(rx_id, tx_id, data)
            await asyncio.sleep(period)

    def close(self):
        for sock in self.connections.values():
            try:
                sock.close()
            except Exception:
                pass

        self.connections.clear()
        print("Closed CAN connection")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.close()