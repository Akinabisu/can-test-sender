import asyncio
import aioisotp

class CANSender:
    def __init__(self, interface: str = 'virtual', channel: str = 'vcan0'):
        self.network = aioisotp.ISOTPNetwork(
            channel=channel, 
            interface=interface
        )

    async def send(self, rx_id: int, tx_id: int, data: bytes):
        reader, writer = await self.network.open_connection(rx_id, tx_id)
        
        try:
            writer.write(data)
            await writer.drain()
        finally:
            writer.close()

    async def sendPeriodically(self, rx_id: int, tx_id:int, data: bytes, period: int):
        while (True):
            await self.send(rx_id, tx_id, data)
            await asyncio.sleep(period)

    def close(self):
        self.network.close()

    async def __aenter__(self):
        self.network.open()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.close()