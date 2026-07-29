import asyncio
import aioisotp

RX_TXT = 0x700
TX_TXT = 0x701

RX_I2C = 0x702
TX_I2C = 0x703

async def dummyReceiver(rx_id, tx_id):
    network = aioisotp.ISOTPNetwork(interface="socketcan", channel="vcan0")
    network.open()
    
    reader, writer = await network.open_connection(rx_id, tx_id)
    print("Receiver waiting for ISO-TP transfer...")
    
    data = await reader.read()
    print(f"Received {len(data)} bytes successfully!")
    network.close()

async def main():
    receiver_txt = asyncio.create_task(dummyReceiver(RX_TXT, TX_TXT))
    receiver_i2c = asyncio.create_task(dummyReceiver(RX_I2C, TX_I2C))                 
    await asyncio.gather(receiver_txt, receiver_i2c)

if __name__ == "__main__":
    asyncio.run(main())