import logging

logger = logging.getLogger(__name__)

class BufferEditor:
    @staticmethod
    def edit_buffer(buffer: str, chunk_size: int = 4) -> str:
        if not isinstance(buffer, str):
            logger.error(f"Expected str, got '{type(buffer).__name__}'")
            raise TypeError(f"edit_buffer requires a string, got {type(buffer).__name__}")

        if chunk_size <= 0:
            logger.error(f"Invalid chunk_size {chunk_size}. Must be greater than 0.")
            raise ValueError("chunk_size must be a positive integer")

        formatted_buffer = " ".join(buffer[i : i + chunk_size] for i in range(0, len(buffer), chunk_size))
        logger.debug(f"Formatted string buffer of length {len(buffer)} into chunks of {chunk_size}")
        
        return formatted_buffer