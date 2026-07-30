import asyncio
import socket
import isotp


RX_TXT = 0x700
TX_TXT = 0x701

RX_I2C = 0x702
TX_I2C = 0x703


async def dummy_receiver(rx_id: int, tx_id: int):
    sock = isotp.socket(timeout=0.5)

    addr = isotp.Address(
        rxid=tx_id,
        txid=rx_id,
    )

    sock.bind("vcan0", address=addr)

    print(
        f"Receiver started: "
        f"RX=0x{tx_id:X}, TX=0x{rx_id:X}"
    )

    loop = asyncio.get_running_loop()

    try:
        while True:
            try:
                data = await loop.run_in_executor(
                    None,
                    sock.recv
                )

                print(
                    f"[0x{tx_id:X}] "
                    f"Received {len(data)} bytes successfully!"
                )
                print(f"Data: {data!r}")

            except socket.timeout:
                continue

    except asyncio.CancelledError:
        print(
            f"Receiver 0x{tx_id:X} shutting down..."
        )
        raise

    finally:
        sock.close()


async def main():
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
