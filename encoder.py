class Encoder:
    @staticmethod
    def encode(data: str) -> bytes:
        return data.encode('ascii')