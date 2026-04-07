import logging
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

import requests
from requests.exceptions import HTTPError

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("Extractor")

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
TEMP_DIR = BASE_DIR / "temp"


class Extract:
    """
    Extracts and downloads files from a given URL, parsing XML responses to locate
    download links.
    """

    def __init__(self, url: str, **kwargs: Any) -> None:
        """
        Initialize the Extract class.

        Args:
            url (str): The URL to fetch data from.
            **kwargs: Additional keyword arguments for requests.
        """
        self.url = url
        self.kwargs = kwargs
        logger.info("Initialized Extract class for URL: %s", self.url)

    def _get(self, url: str, **kwargs: Any) -> requests.Response:
        """
        Perform a GET request to the specified URL.

        Args:
            url (str): The URL to send the GET request to.
            **kwargs: Additional keyword arguments for requests.

        Returns:
            requests.Response: The HTTP response object.
        """
        logger.debug("Attempting GET request to: %s", url)
        return requests.get(url, **kwargs)

    def _parse_xml(
        self, xml_response: str, link_indx: int = 2, atrib: str = "download_link"
    ) -> str:
        """
        Parse the XML response to extract a download link.

        Args:
            xml_response (str): The XML response as a string.
            link_indx (int): The index of the document to extract the link from.
            atrib (str): The attribute name to look for in the XML.

        Returns:
            str: The extracted download link.

        Raises:
            ValueError: If the XML is missing required tags or the index is out of
                range.
            KeyError: If required attributes are missing.
        """
        logger.info("Parsing XML response to find index %d", link_indx)
        root = ET.fromstring(xml_response)
        response_result = root.find("result")
        if response_result is None:
            logger.error("XML missing 'result' tag")
            raise ValueError("Error extracting result form the XML Response")

        result_atrib = response_result.attrib
        num_found = result_atrib.get("numFound")

        if num_found is None:
            logger.error("XML result missing 'numFound' attribute")
            raise KeyError(
                f"Failed to retrive atributes from result: numFound {num_found}"
            )

        if link_indx >= int(num_found):
            logger.warning(
                "Requested index %d but only %s docs found", link_indx, num_found
            )
            raise ValueError("Link Index is higher than the number of docs in result")

        response_docs = response_result.findall("doc")
        choosen_doc = response_docs[link_indx]

        zip_link = choosen_doc.find(f"str[@name='{atrib}']")
        if zip_link is None:
            logger.error("Target attribute '%s' not found in document", atrib)
            raise KeyError(f"The tag 'str[@name={atrib}]' does not exists")

        if zip_link.text:
            logger.info("Successfully extracted download link.")
            return zip_link.text
        return ""

    def _save_to_disk(
        self, response: requests.Response, file_name: str = "test"
    ) -> None:
        """
        Save the content of the response to disk as a zip file.

        Args:
            response (requests.Response): The HTTP response containing the file content.
            file_name (str): The name of the file to save (without extension).
        """
        TEMP_DIR.mkdir(exist_ok=True)
        file_path = TEMP_DIR / f"{file_name}.zip"

        logger.info("Saving file to %s", "temp/test.zip")
        with open(file_path, "wb") as zip_file:
            zip_file.write(response.content)

    def _clean_disk(self):
        """
        Placeholder for disk cleanup logic.
        """
        # TODO: NEED TO IMPLEMENT NOT SURE WHERE
        # MAYBE I SHOULD CREATE A GARBAGE COLLECTOR TO CLEAN THE DISK
        logger.warning("Work in progress (_clean_disk)")

    def run(self):
        """
        Execute the extraction process: fetch XML, parse for download link, download
            file, and save to disk.

        Raises:
            HTTPError: If any HTTP request fails.
        """
        response = self._get(self.url, **self.kwargs)
        if response.status_code != 200:
            raise HTTPError(f"Status Code: {response.status_code}, URL: {self.url}")

        download_link = self._parse_xml(response.text, 2, "download_link")

        logger.info("Downloading zip file...")
        response = self._get(download_link, **self.kwargs)
        if response.status_code != 200:
            raise HTTPError(
                f"Status Code: {response.status_code}, URL: {download_link}"
            )

        self._save_to_disk(response)

        # WARNING: IT IS NOT DOING ANYTHING(NOT IMPLEMENTED)
        self._clean_disk()


def main():
    """
    Used mainly for testing and developing
    """
    url = (
        "https://registers.esma.europa.eu/solr/esma_registers_firds_files/select?"
        "q=*&fq=publication_date:[2021-01-17T00:00:00Z+TO+2021-01-19T23:59:59Z]"
        "&wt=xml&indent=true&start=0&rows=100"
    )
    extract = Extract(url)
    extract.run()


if __name__ == "__main__":
    main()
