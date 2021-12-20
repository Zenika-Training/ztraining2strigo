# coding: utf8

import http.client
from functools import lru_cache

from ..models.errors import Error

_CONNECTION = http.client.HTTPSConnection('raw.githubusercontent.com')
_REPOSITORY = 'Zenika/strigo-init-script-libs'


@lru_cache(maxsize=None)
def retrieve_script(script: str, version: str, folder: str) -> str:
    _CONNECTION.connect()
    url = f"/{_REPOSITORY}/{version}/{folder}/{script}"
    _CONNECTION.request('GET', url)
    response = _CONNECTION.getresponse()
    raw_data = response.read()
    charset = response.headers.get_content_charset()
    if raw_data and charset:
        data = raw_data.decode(charset)
    if response.status != http.client.OK:
        message = f"{url}: {response.status} {response.reason}"
        if data:
            message += f" -> {data}"
        raise Error(type='HTTPError', message=message)
    return data
