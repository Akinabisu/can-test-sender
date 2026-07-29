class BufferEditor:
    
    @staticmethod
    def editBuffer(buffer):
        return " ".join(buffer[i : i + 4] for i in range(0, len(buffer), 4))