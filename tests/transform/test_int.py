import pandas as pd
from steeleye.transform.main import Transform, TEMP_DIR
import zipfile


def test_transform_run_pipeline(tmp_path):
    xml_content = """
    <Document xmlns="urn:iso:std:iso:20022:tech:xsd:auth.036.001.02">
      <FinInstrm>
        <Record>
            <FinInstrmGnlAttrbts>
            <Id>123</Id>
            <FullNm>alpha</FullNm>
            <ClssfctnTp>type</ClssfctnTp>
            <CmmdtyDerivInd>Y</CmmdtyDerivInd>
            <NtnlCcy>USD</NtnlCcy>
            </FinInstrmGnlAttrbts>
            <Issr>issuer</Issr>
        </Record>
      </FinInstrm>
    </Document>
    """
    xml_file = tmp_path / "test.xml"
    xml_file.write_text(xml_content)
    zip_file = TEMP_DIR / "test.zip"

    with zipfile.ZipFile(zip_file, "w") as zf:
        zf.write(xml_file, arcname="test.xml")

    t = Transform()
    df = t.run()
    assert not df.empty
    assert "a_count" in df.columns
    assert df.iloc[0]["FullNm"] == "alpha"
    if zip_file.exists():
        zip_file.unlink()
    if xml_file.exists():
        xml_file.unlink()
