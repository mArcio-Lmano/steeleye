import requests
import xml.etree.ElementTree as ET
from requests.exceptions import HTTPError


class XMLClient:
    def __init__(self):
        pass

    def _get(self, url, **kwargs):
        x = requests.get(url, kwargs)
        return x

    def _parse_xml(self, xml_response, link_indx, atrib):
        root = ET.fromstring(xml_response)
        response_result = root.find("result")
        if response_result is None:
            raise ValueError("Error extracting result form the XML Response")
        result_atrib = response_result.attrib
        numFound = result_atrib.get("numFound")

        if numFound is None:
            raise KeyError(
                f"Failed to retrive atributes from result: numFound {numFound}"
            )

        if link_indx >= int(numFound):
            raise ValueError("Link Index is higher than the number of docs in result")

        response_docs = response_result.findall("doc")
        choosen_doc = response_docs[link_indx]
        return choosen_doc.find(f"str[@name='{atrib}']").text


def main():
    xml_client = XMLClient()
    response = xml_client._get(
        "https://registers.esma.europa.eu/solr/esma_registers_firds_files/select?q=*&fq=publication_date:[2021-01-17T00:00:00Z+TO+2021-01-19T23:59:59Z]&wt=xml&indent=true&start=0&rows=100"
    )
    if response.status_code != 200:
        raise HTTPError(f"Status Code: {response.status_code}")
    download_link = xml_client._parse_xml(response.text, 2, "download_link")
    print(download_link)
    x = xml_client._get(download_link)
    with open("temp/test.zip", "wb") as zip_file:
        zip_file.write(x.content)


if __name__ == "__main__":
    main()
