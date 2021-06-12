# coding: utf8
from __future__ import annotations
from email import message

import http.client
import json
import os
import uuid
from pathlib import Path
from typing import Any, Dict, List, Type, TypeVar, Union
from urllib.parse import urlparse

from .models.errors import Error, RequestValidationError

_T = TypeVar('_T')


class Client:

    def __init__(self, organization_id: str, api_key: str, strigo_endpoint: str = 'https://app.strigo.io/api/v1') -> None:
        parse_result = urlparse(strigo_endpoint)
        if parse_result.scheme == 'https':
            self._connection = http.client.HTTPSConnection(parse_result.hostname, parse_result.port)
        else:
            self._connection = http.client.HTTPConnection(parse_result.hostname, parse_result.port)
        if bool(os.environ.get('Z2S_TRACE_HTTP', False)):
            self._connection.set_debuglevel(1)
        self._path = parse_result.path
        self._token = f"{organization_id}:{api_key}"

    def _headers(self):
        return {
            'Authorization': f"Bearer {self._token}",
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def get(self, path: str, cls: Type[_T]) -> Union[_T, List[_T]]:
        self._connection.connect()
        self._connection.request('GET', f"{self._path}{path}", headers=self._headers())
        response = self._connection.getresponse()
        raw_data = response.read()

        self._handle_raw_error(response, raw_data)

        return self._parse_result(response, raw_data, cls)

    def post(self, path, data: Dict[str: Any], cls: Type[_T]) -> _T:
        self._connection.connect()
        body = json.dumps(data)
        self._connection.request('POST', f"{self._path}{path}", body=body, headers=self._headers())
        response = self._connection.getresponse()
        raw_data = response.read()

        self._handle_raw_error(response, raw_data)

        return self._parse_result(response, raw_data, cls)

    def patch(self, path, data: Dict[str: Any], cls: Type[_T]) -> _T:
        self._connection.connect()
        body = json.dumps(data)
        self._connection.request('PATCH', f"{self._path}{path}", body=body, headers=self._headers())
        response = self._connection.getresponse()
        raw_data = response.read()

        self._handle_raw_error(response, raw_data)

        return self._parse_result(response, raw_data, cls)

    def upload(self, path, data: Dict[str: Path], cls: Type[_T]) -> _T:
        self._connection.connect()
        headers = self._headers()
        boundary = uuid.uuid4().hex
        headers['Content-Type'] = f"multipart/form-data; boundary={boundary}"

        def body() -> bytes:
            for name, filepath in data.items():
                yield f"\r\n--{boundary}\r\n".encode('ascii')
                yield f"Content-Disposition: form-data; name=\"{name}\"; filename=\"{filepath.name}\"\r\n".encode('ascii')
                yield f"Content-Type: application/octet-stream\r\n".encode('ascii')
                yield '\r\n'.encode('ascii')
                with filepath.open('rb') as f:
                    for chunk in iter(lambda: f.read(1024 * 8), b''):
                        yield chunk
            yield f"\r\n--{boundary}--".encode('ascii')

        self._connection.request('POST', f"{self._path}{path}", body=body(), headers=headers)
        response = self._connection.getresponse()
        raw_data = response.read()

        self._handle_raw_error(response, raw_data)

        return self._parse_result(response, raw_data, cls)

    def delete(self, path) -> None:
        self._connection.connect()
        self._connection.request('DELETE', f"{self._path}{path}", headers=self._headers())
        response = self._connection.getresponse()
        raw_data = response.read()

        self._handle_raw_error(response, raw_data, [http.client.NO_CONTENT])

    def _handle_raw_error(self, response: http.client.HTTPResponse, raw_data: bytes, expected_statuses: List[int] = [http.client.OK, http.client.UNPROCESSABLE_ENTITY]) -> None:
        if self._connection.debuglevel > 0:
            print("reply:", repr(raw_data))
        try:
            data = json.loads(raw_data)
            if data['result'] == 'failure':
                return  # Higher level error
        except Exception:
            pass
        if response.status not in expected_statuses:
            message = f"{response.status} {response.reason}"
            charset = response.headers.get_content_charset()
            if raw_data and charset:
                data = raw_data.decode(charset)
                message += f" -> {data}"
            raise Error(type='HTTPError', message=message)

    def _parse_result(self, response: http.client.HTTPResponse, raw_data: bytes, cls: Type[_T]) -> _T:
        data = json.loads(raw_data)

        if data['result'] == 'success':
            if isinstance(data['data'], list):
                return [cls.from_dict(e) for e in data['data']]
            else:
                return cls.from_dict(data['data'])
        elif data['result'] == 'failure':
            if response.status == http.client.UNPROCESSABLE_ENTITY:
                raise RequestValidationError.from_dict(data['error'])
            else:
                raise Error.from_dict(data['error'])
        else:
            raise Exception()  # FIXME: unexpected format
