import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class FileReader:
    @staticmethod
    def read(file_path: Path | str, encoding: str = "ascii") -> str:
        target_path = Path(file_path)
        
        try:
            content = target_path.read_text(encoding=encoding)
            logger.info(f"Successfully read: '{target_path}' ({len(content)} characters)")
            return content

        except FileNotFoundError:
            logger.exception(f"File not found: '{target_path}'")
            raise
        except PermissionError:
            logger.exception(f"Permission denied when reading: '{target_path}'")
            raise
        except Exception:
            logger.exception(f"Failed to read :'{target_path}'")
            raise