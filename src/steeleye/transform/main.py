from zipfile import ZipFile
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("Extractor")

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
TEMP_DIR = BASE_DIR / "temp"


class Transform:
    def __init__(self) -> None:
        pass

    def _extract_zip(self, file_name):
        TEMP_DIR.mkdir(exist_ok=True)
        zip_path = TEMP_DIR / file_name

        with ZipFile(zip_path, "r") as zObject:
            zObject.extractall(path=TEMP_DIR)


def main():
    transform = Transform()
    transform._extract_zip("test.zip")


if __name__ == "__main__":
    main()
