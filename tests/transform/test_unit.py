import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from steeleye.transform.main import Transform, TEMP_DIR


def test_count_a_adds_column():
    df = pd.DataFrame({"FullNm": ["aaa", "abc", "xyz"]})
    result = Transform()._count_a(df)
    assert "a_count" in result.columns
    assert result["a_count"].tolist() == [3, 1, 0]


@patch("steeleye.transform.main.ZipFile")
def test_extract_zip_success(mock_zip):
    mock_zip.return_value.__enter__.return_value.namelist.return_value = [
        "file1.xml",
        "file2.xml",
    ]
    t = Transform()
    files = t._extract_zip("test.zip")
    assert all(str(f).endswith(".xml") for f in files)
    assert len(files) == 2


@patch("steeleye.transform.main.ET.parse")
def test_covert_to_df_parses_xml(mock_parse):
    mock_root = MagicMock()
    mock_instr = MagicMock()
    mock_record = MagicMock()
    mock_attr = MagicMock()
    mock_attr.findtext.side_effect = ["id", "full", "clssf", "cmdty", "ccy"]
    mock_record.find.return_value = mock_attr
    mock_record.findtext.return_value = "issuer"
    mock_instr.__iter__.return_value = [mock_record]
    mock_root.findall.return_value = [mock_instr]
    mock_parse.return_value.getroot.return_value = mock_root

    t = Transform()
    df = t._covert_to_df([TEMP_DIR / "file.xml"])
    assert not df.empty
    assert set(df.columns) >= {
        "Id",
        "FullNm",
        "ClssfctnTp",
        "CmmdtyDerivInd",
        "NtnlCcy",
        "Issr",
    }


@patch("steeleye.transform.main.ET.parse", side_effect=Exception("parse error"))
def test_covert_to_df_parse_error(mock_parse):
    t = Transform()
    with pytest.raises(RuntimeError):
        t._covert_to_df([TEMP_DIR / "bad.xml"])
