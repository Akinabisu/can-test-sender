import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class FileReader:
    @staticmethod
    def read(file_path: Path | str ) -> str:
        target_path = Path(file_path)
        
        try:
            content = target_path.read_text(encoding="ascii")
            logging.info(f"Successfully read: '{target_path}', length: {len(content)} characters")
            return content

        except FileNotFoundError:
            logging.error(f"File not found: '{target_path}'")
            raise
        except PermissionError:
            logging.error(f"Permission denied when reading: '{target_path}'")
            raise
        except Exception as e:
            logging.error(f"Failed to read :'{target_path}': {e}")
            raise