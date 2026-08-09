# mocks/i2c_scanner_mock.py
import logging

logger = logging.getLogger(__name__)

class I2CScannerMock:
    @staticmethod
    def scan(bus_number: int = 1, active_addresses: list[int] = [0x3C, 0x68]) -> list[int]:
        logging.info(f"[MOCK]Scanning I2C bus /dev/i2c-{bus_number}...")
        return active_addresses

    @staticmethod
    def scan_to_str(bus_number: int = 1) -> str:
        detected_addresses = I2CScannerMock.scan(bus_number)

        lines = ["     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f"]

        for row in range(0x00, 0x80, 0x10):
            line = f"{row:02x}: "
            for col in range(0x10):
                addr = row + col

                if addr < 0x08 or addr > 0x77:
                    line += "   "
                elif addr in detected_addresses:
                    line += f"{addr:02x} "
                else:
                    line += "-- "

            lines.append(line)

        return "\n".join(lines)