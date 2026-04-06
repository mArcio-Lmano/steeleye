import os
import pytest
from steeleye.extract.main import Extract


@pytest.mark.integration
def test_extract_real_url():
    url = (
        "https://registers.esma.europa.eu/solr/esma_registers_firds_files/select?"
        "q=*&fq=publication_date:[2021-01-17T00:00:00Z+TO+2021-01-19T23:59:59Z]"
        "&wt=xml&indent=true&start=0&rows=100"
    )

    file_path = "temp/test.zip"

    if os.path.exists(file_path):
        os.remove(file_path)

    extract_instance = Extract(url)
    extract_instance.run()

    assert os.path.exists(file_path), "File was not created on disk"
    assert os.path.getsize(file_path) > 0, "Downloaded file is empty"
