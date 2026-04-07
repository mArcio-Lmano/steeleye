import pathlib
import pytest
from unittest.mock import patch, MagicMock, mock_open
from requests.exceptions import HTTPError
from steeleye.extract import Extract
from pathlib import Path


def test_parse_xml_success():
    xml_data = """
    <response>
        <result numFound="3">
            <doc><str name="download_link">http://link0.com</str></doc>
            <doc><str name="download_link">http://link1.com</str></doc>
            <doc><str name="download_link">http://link2.com</str></doc>
        </result>
    </response>
    """
    extractor = Extract("http://fake.com")
    result = extractor._parse_xml(xml_data, 2, "download_link")
    assert result == "http://link2.com"


def test_parse_xml_out_of_bounds():
    xml_data = '<response><result numFound="1"><doc></doc></result></response>'
    extractor = Extract("http://fake.com")
    with pytest.raises(ValueError, match="Link Index is higher"):
        extractor._parse_xml(xml_data, 5, "any")


@patch("steeleye.extract.main.TEMP_DIR")
@patch("builtins.open", new_callable=mock_open)
def test_save_to_disk_dynamic_name(mock_file, mock_temp_dir):
    mock_temp_dir.__truediv__.return_value = Path("/fake/path/test.zip")
    extractor = Extract("http://fake.com")
    mock_response = MagicMock(content=b"data")

    extractor._save_to_disk(mock_response, file_name="test")

    mock_file.assert_called_once_with(Path("/fake/path/test.zip"), "wb")
    mock_file().write.assert_called_once_with(b"data")


@patch.object(Extract, "_get")
@patch.object(Extract, "_parse_xml")
@patch.object(Extract, "_save_to_disk")
def test_run_workflow_coordination(mock_save, mock_parse, mock_get):
    extractor = Extract("http://start.com")

    mock_resp_xml = MagicMock(status_code=200, text="some_xml")
    mock_resp_zip = MagicMock(status_code=200, content=b"zip_data")
    mock_get.side_effect = [mock_resp_xml, mock_resp_zip]

    mock_parse.return_value = "http://download.com"

    extractor.run()

    assert mock_get.call_count == 2
    mock_parse.assert_called_once_with("some_xml", 2, "download_link")
    mock_save.assert_called_once_with(mock_resp_zip)


@patch.object(Extract, "_get")
def test_run_http_error_handling(mock_get):
    extractor = Extract("http://not-found-url.com")
    mock_get.return_value = MagicMock(status_code=404)

    with pytest.raises(HTTPError):
        extractor.run()
