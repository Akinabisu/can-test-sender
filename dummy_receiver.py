import asyncio
import aioisotp

RX = 0x701
TX = 0x700

async def dummyReceiver():
    network = aioisotp.ISOTPNetwork(interface="socketcan", channel="vcan0")
    network.open()
    
    reader, writer = await network.open_connection(RX, TX)
    print("Receiver waiting for ISO-TP transfer...")
    
    data = await reader.read()
    print(f"Received {len(data)} bytes successfully!")
    network.close()

if __name__ == "__main__":
    asyncio.run(dummyReceiver())