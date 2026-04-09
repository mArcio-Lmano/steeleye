from zipfile import ZipFile

import xml.etree.ElementTree as ET
import logging
from pathlib import Path
import pandas as pd

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("Transform")

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
TEMP_DIR = BASE_DIR / "temp"


class Transform:
    def __init__(
        self, ns: dict = {"schema": "urn:iso:std:iso:20022:tech:xsd:auth.036.001.02"}
    ) -> None:
        self.ns = ns

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
                count += 1
                if count > 40:
                    break

    def _discover_records_type(self, extracted_files) -> list:
        found_record_types = set()

        for files_count, file in enumerate(extracted_files, 1):
            try:
                tree = ET.parse(file)
                root = tree.getroot()
            except Exception as e:
                logger.error("Failed to parse %s: %s", file, e)
                continue

            for instr in root.findall(".//schema:FinInstrm", self.ns):
                child = instr[0]
                tag_name = child.tag.split("}")[-1]
                found_record_types.add(tag_name)

        return list(found_record_types)

    def _covert_to_df(self, extracted_files: list[Path]) -> pd.DataFrame:
        root = None
        rows = []
        files_count = 0
        for file in extracted_files:
            files_count += 1
            logger.info("Processing file %s: %s", files_count, file.name)

            try:
                tree = ET.parse(file)
                root = tree.getroot()
            except Exception as e:
                raise RuntimeError(
                    "The xml File %s was not parsed correctly: %s", file, e
                )

            try:
                for instr in root.findall(".//schema:FinInstrm", self.ns):
                    record = next(child for child in instr)

                    if record is not None:
                        attributes = record.find("schema:FinInstrmGnlAttrbts", self.ns)

                        row = {}
                        if attributes is not None:
                            row["Id"] = attributes.findtext(
                                "schema:Id", default="", namespaces=self.ns
                            )
                            row["FullNm"] = attributes.findtext(
                                "schema:FullNm", default="", namespaces=self.ns
                            )
                            row["ClssfctnTp"] = attributes.findtext(
                                "schema:ClssfctnTp", default="", namespaces=self.ns
                            )
                            row["CmmdtyDerivInd"] = attributes.findtext(
                                "schema:CmmdtyDerivInd", default="", namespaces=self.ns
                            )
                            row["NtnlCcy"] = attributes.findtext(
                                "schema:NtnlCcy", default="", namespaces=self.ns
                            )

                        row["Issr"] = record.findtext(
                            "schema:Issr", default="", namespaces=self.ns
                        )

                        rows.append(row)
            except Exception as e:
                logger.critical("Critical Issue parsing file: %s, %s", file, e)

        return pd.DataFrame(rows)

    def _count_a(self, df: pd.DataFrame) -> pd.DataFrame:
        df["a_count"] = df["FullNm"].fillna("").apply(lambda x: x.count("a"))
        return df


def main():
    transform = Transform()
    files = transform._extract_zip("test.zip")
    df = transform._covert_to_df(files)
    df = transform._count_a(df)
    print(df.head(5))


if __name__ == "__main__":
    main()
