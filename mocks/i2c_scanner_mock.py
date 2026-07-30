class I2CScannerMock:
    @staticmethod
    def scan(detected_addresses: set[int] = {0x3C, 0x68}) -> str:
        lines = ["     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f"]
        
        for row in range(0x00, 0x80, 0x10):
            line = f"{row:02x}: "
            for col in range(0x10):
                addr = row + col

                if addr < 0x08 or addr > 0x77:
                    line += "   "
                    continue

                if addr in detected_addresses:
                    line += f"{addr:02x} "
                else:
                    line += "-- "

            lines.append(line)

        return "\n".join(lines)