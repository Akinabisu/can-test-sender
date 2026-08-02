from smbus2 import SMBus

class I2CScanner:
    @staticmethod
    def scan(bus_number: int = 1) -> str:
        lines = ["     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f"]
        
        try:
            with SMBus(bus_number) as bus:
                for row in range(0x00, 0x80, 0x10):
                    line = f"{row:02x}: "
                    for col in range(0x10):
                        addr = row + col

                        if addr < 0x08 or addr > 0x77:
                            line += "   "
                            continue

                        try:
                            bus.write_quick(addr)
                            line += f"{addr:02x} "
                        except OSError:
                            line += "-- "

                    lines.append(line)
        except FileNotFoundError:
            return f"Error: I2C bus /dev/i2c-{bus_number} not found."
        except PermissionError:
            return f"Error: Permission denied accessing /dev/i2c-{bus_number}. Try running with sudo."

        lines = "\n".join(lines)
        
        print(f"Scanned I2C, Result: \n{lines}")
        return lines