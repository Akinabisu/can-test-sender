import asyncio
import aioisotp

async def dummyReceiver():
    network = aioisotp.ISOTPNetwork(interface="socketcan", channel="vcan0")
    network.open()
    
    reader, writer = await network.open_connection(0x7E0, 0x7E8)
    print("Receiver waiting for ISO-TP transfer...")
    
    data = await reader.read()
    print(f"Received {len(data)} bytes successfully!")
    network.close()

if __name__ == "__main__":
    asyncio.run(dummyReceiver())