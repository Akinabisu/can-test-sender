# mocks/i2c_scanner_mock.py
import logging

logger = logging.getLogger(__name__)

class I2CScannerMock:

    @staticmethod
    def scan_to_str() -> str:
        detected_addresses = set({0x3C, 0x68})

        logger.info("[MOCK] Performing virtual I2C scan...")
        
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