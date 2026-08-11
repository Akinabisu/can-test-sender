import logging
from smbus2 import SMBus

logger = logging.getLogger(__name__)

class I2CScanner:
    @staticmethod
    def scan(bus_number: int = 1) -> list[int]:
        active_addresses = []
        logger.info(f"Scanning I2C bus /dev/i2c-{bus_number}...")

        try:
            with SMBus(bus_number) as bus:
                for addr in range(0x08, 0x78):
                    try:
                        bus.write_quick(addr)
                        active_addresses.append(addr)
                    except OSError:
                        # Expected when no device; ignore and continue scanning
                        pass
        except FileNotFoundError:
            logger.exception(f"I2C bus /dev/i2c-{bus_number} not found.")
            raise
        except PermissionError:
            logger.exception(f"Permission denied accessing /dev/i2c-{bus_number}.")
            raise
        except Exception:
            logger.exception(f"Error scanning I2C bus {bus_number}")
            raise

        logger.info(f"Scan complete on bus {bus_number}. Found {len(active_addresses)} device(s).")
        return active_addresses

    @staticmethod
    def scan_to_str(bus_number: int = 1) -> str:
        detected_addresses = I2CScanner.scan(bus_number)
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

        lines = "\n".join(lines)

        logger.info(f"Scanned I2C, Result: \n{lines}")
        return lines