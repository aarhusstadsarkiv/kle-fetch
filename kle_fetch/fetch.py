from http.client import HTTPException
from http.client import HTTPResponse
from urllib.request import urlopen

import xmltodict as xml

URL_EMNER = "https://api.kle-online.dk/resources/kle/emneplan?udgaaede=true"
URL_FACETTER = "https://api.kle-online.dk/resources/kle/handlingsfacetter?udgaaede=true"


def fetch_xml(url: str) -> dict:
    response: HTTPResponse = urlopen(url)
    if response.status != 200:
        raise HTTPException(response.geturl(), response.status)
    return xml.parse(response.read())


def fetch_emner() -> dict:
    return fetch_xml(URL_EMNER)


def fetch_facetter() -> dict:
    return fetch_xml(URL_FACETTER)
