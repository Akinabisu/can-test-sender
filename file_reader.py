import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class FileReader:
    @staticmethod
    def read(file_path: Path | str, encoding: str = "utf-8") -> str:
        target_path = Path(file_path)
        
        try:
            content = target_path.read_text(encoding=encoding)
            logger.info(f"Successfully read: '{target_path}', length: {len(content)} characters")
            return content

        except FileNotFoundError:
            logger.error(f"File not found: '{target_path}'")
            raise
        except IsADirectoryError:
            logger.error(f"Expected a file, but target path is a directory: '{target_path}'")
            raise
        except PermissionError:
            logger.error(f"Permission denied when reading: '{target_path}'")
            raise
        except UnicodeDecodeError as e:
            logger.error(f"Failed to decode file '{target_path}' using '{encoding}' encoding: {e}")
            raise
        except OSError as e:
            logger.error(f"OS error occurred while reading '{target_path}': {e}")
            raise