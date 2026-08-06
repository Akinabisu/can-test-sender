import os
import asyncio
import can
import isotp

RX_TXT = 0x700
TX_TXT = 0x701

RX_I2C = 0x702
TX_I2C = 0x703


async def dummy_receiver(
    rx_id: int, 
    tx_id: int, 
):
    channel = os.getenv("CAN_CHANNEL", "vcan0")
    interface = os.getenv("CAN_INTERFACE", "socketcan")

    bus = can.interface.Bus(channel=channel, bustype=interface)

    address = isotp.Address(rxid=tx_id, txid=rx_id)

    stack = isotp.CanStack(
        bus=bus,
        address=address,
        params={'stmin': 5, 'blocksize': 8, 'tx_data_length': 8}
    )

    print(f"Receiver started on '{channel}' ({interface}): RX=0x{tx_id:03X}, TX=0x{rx_id:03X}")

    try:
        while True:
            # Step the ISO-TP state machine (sends Flow Control frames automatically)
            stack.process()

            if stack.available():
                data = stack.recv()
                print(f"\n[0x{tx_id:03X}] Received {len(data)} bytes successfully!")
                print(f"Data: {data!r}")

            # Yield control back to asyncio event loop
            await asyncio.sleep(0.005)

    except asyncio.CancelledError:
        print(f"Receiver 0x{tx_id:03X} shutting down...")
        raise
    finally:

        if not bus:
            bus.shutdown()


async def main():
    channel = os.getenv("CAN_CHANNEL", "test_channel")
    interface = os.getenv("CAN_INTERFACE", "virtual")

    if interface == "virtual":
        shared_bus = can.interface.Bus(channel=channel, bustype="virtual")

    receiver_txt = asyncio.create_task(
        dummy_receiver(RX_TXT, TX_TXT)
    )

    receiver_i2c = asyncio.create_task(
        dummy_receiver(RX_I2C, TX_I2C)
    )

    await asyncio.gather(
        receiver_txt,
        receiver_i2c,
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nDummy receiver stopped.")