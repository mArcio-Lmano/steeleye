import logging
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile

import pandas as pd

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("Transform")

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
TEMP_DIR = BASE_DIR / "temp"


class Transform:
    """
    Handles extraction, parsing, and transformation of ISO 20022 XML files.
    """

    def __init__(
        self, ns: dict = {"schema": "urn:iso:std:iso:20022:tech:xsd:auth.036.001.02"}
    ) -> None:
        """
        Initialize the Transform class with XML namespaces.

        Args:
            ns (dict): XML namespaces for parsing. Defaults to ISO 20022 schema.
        """
        self.ns = ns

    def _extract_zip(self, file_name) -> list[Path]:
        """
        Extracts all files from a ZIP archive into a temporary directory.

        Args:
            file_name (str): Name of the ZIP file to extract.

        Returns:
            list[Path]: List of extracted file paths.

        Raises:
            FileNotFoundError: If the ZIP file is not found.
        """
        TEMP_DIR.mkdir(exist_ok=True)
        zip_path = TEMP_DIR / file_name
        try:
            with ZipFile(zip_path, "r") as zObject:
                zObject.extractall(path=TEMP_DIR)
                extracted_files = [TEMP_DIR / name for name in zObject.namelist()]
            return extracted_files
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Failed to find zip: {e}")

    def _covert_to_df(self, extracted_files: list[Path]) -> pd.DataFrame:
        """
        Converts extracted XML files into a pandas DataFrame.

        Args:
            extracted_files (list[Path]): List of extracted XML file paths.

        Returns:
            pd.DataFrame: DataFrame containing parsed XML data.

        Raises:
            RuntimeError: If an XML file cannot be parsed.
        """
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
        """
        Adds a column counting occurrences of 'a' in the 'FullNm' field.

        Args:
            df (pd.DataFrame): Input DataFrame.

        Returns:
            pd.DataFrame: DataFrame with an added 'a_count' column.
        """
        df["a_count"] = df["FullNm"].fillna("").apply(lambda x: x.count("a"))
        return df

    def run(self) -> pd.DataFrame:
        """
        Runs the full transformation pipeline: extraction, parsing, and transformation.

        Returns:
            pd.DataFrame: Final DataFrame with extracted and processed data.
        """
        files = self._extract_zip("test.zip")
        df = self._covert_to_df(files)
        df = self._count_a(df)
        return df


def main():
    transform = Transform()
    df = transform.run()
    print(df.head(5))


if __name__ == "__main__":
    main()
