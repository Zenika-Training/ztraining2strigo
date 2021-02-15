# coding: utf8
from __future__ import annotations

from typing import List, Union

from ..client import Client
from ..models.classes import Class
from . import UNDEFINED, UNDEFINED_TYPE


def list(client: Client) -> List[Class]:
    return client.get('/classes', Class)


def search(client: Client, name: str) -> List[Class]:
    return [cls for cls in list(client) if cls.name == name]


def get(client: Client, class_id: str) -> Class:
    return client.get(f"/classes/{class_id}", Class)


def create(client: Client, name: str, description: Union[str, UNDEFINED_TYPE] = UNDEFINED) -> Class:
    data = {'name': name}
    if description is not UNDEFINED:
        data['description'] = description
    return client.post('/classes', data, Class)


def update(client: Client, class_id: str, name: Union[str, UNDEFINED_TYPE] = UNDEFINED, description: Union[str, UNDEFINED_TYPE] = UNDEFINED) -> Class:
    data = {}
    if name is not UNDEFINED:
        data['name'] = name
    if description is not UNDEFINED:
        data['description'] = description
    return client.patch(f"/classes/{class_id}", data, Class)


def delete(client: Client, class_id: str) -> None:
    client.delete(f"/classes/{class_id}")
