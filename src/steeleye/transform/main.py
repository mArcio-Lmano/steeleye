from zipfile import ZipFile

import xml.etree.ElementTree as ET
import logging
from pathlib import Path
import pandas as pd

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("Extractor")

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
TEMP_DIR = BASE_DIR / "temp"


class Transform:
    def __init__(self) -> None:
        pass

    def _extract_zip(self, file_name) -> list[Path]:
        TEMP_DIR.mkdir(exist_ok=True)
        zip_path = TEMP_DIR / file_name
        try:
            with ZipFile(zip_path, "r") as zObject:
                zObject.extractall(path=TEMP_DIR)
                extracted_files = [TEMP_DIR / name for name in zObject.namelist()]
            return extracted_files
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Failed to find zip: {e}")

    def _check_tags(self, extracted_files: list[Path]) -> None:
        for file in extracted_files:
            count = 0
            with open(file, "r") as xml:
                root = ET.fromstring(xml.read())
            for elem in root.iter():
                print(elem.tag)
                count += 1
                if count > 40:
                    break

    def _covert_to_df(self, extracted_files: list[Path]) -> pd.DataFrame:
        root = None
        rows = []
        ns = {"schema": "urn:iso:std:iso:20022:tech:xsd:auth.036.001.02"}
        files_count = 0
        for file in extracted_files:
            files_count += 1
            logger.info("Processing file number %s", files_count)
            with open(file, "r") as xml:
                root = ET.fromstring(xml.read())

            if root is None:
                raise RuntimeError("The xml File was not parsed correctly")
            for instr in root.findall(".//schema:FinInstrm", ns):
                row = {}
                atributes = instr.find(".//schema:FinInstrmGnlAttrbts", ns)
                if atributes is not None:
                    row["Id"] = atributes.findtext(
                        "schema:Id", default="", namespaces=ns
                    )
                    row["FullNm"] = atributes.findtext(
                        "schema:FullNm", default="", namespaces=ns
                    )
                    row["ClssfctnTp"] = atributes.findtext(
                        "schema:ClssfctnTp", default="", namespaces=ns
                    )
                    row["CmmdtyDerivInd"] = atributes.findtext(
                        "schema:CmmdtyDerivInd", default="", namespaces=ns
                    )
                    row["NtnlCcy"] = atributes.findtext(
                        "schema:NtnlCcy", default="", namespaces=ns
                    )

                # BUG: Not able to extract Issr
                row["Issr"] = instr.findtext(
                    "schema:Issr", default="NotFound", namespaces=ns
                )

                rows.append(row)

        return pd.DataFrame(rows)

    def _count_a(self, df: pd.DataFrame) -> pd.DataFrame:
        df["a_count"] = df["FullNm"].fillna("").apply(lambda x: x.count("a"))
        return df


def main():
    transform = Transform()
    files = transform._extract_zip("test.zip")
    transform._check_tags(files)
    df = transform._covert_to_df(files)
    df = transform._count_a(df)
    print(df.head(5))


if __name__ == "__main__":
    main()
