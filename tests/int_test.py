import pytest
from steeleye.extract.main import Extract, TEMP_DIR


@pytest.mark.integration
def test_extract_real_url():
    url = (
        "https://registers.esma.europa.eu/solr/esma_registers_firds_files/select?"
        "q=*&fq=publication_date:[2021-01-17T00:00:00Z+TO+2021-01-19T23:59:59Z]"
        "&wt=xml&indent=true&start=0&rows=100"
    )

    file_name = "test"
    file_path = TEMP_DIR / f"{file_name}.zip"

    if file_path.exists():
        file_path.unlink()

    extract_instance = Extract(url)
    extract_instance.run()

    assert file_path.exists(), f"File was not created at {file_path}"
    assert file_path.stat().st_size > 0, "Downloaded file is empty"

    file_path.unlink()
