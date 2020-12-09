# coding: utf8
from __future__ import annotations

from typing import List, Union

from ..client import Client
from ..models.resources import Resource, WebviewLink
from . import UNDEFINED, UNDEFINED_TYPE


def list(client: Client, class_id: str) -> List[Resource]:
    return client.get(f"/classes/{class_id}/resources", Resource)


def get(client: Client, class_id: str, resource_id: str) -> Resource:
    return client.get(f"/classes/{class_id}/resources/{resource_id}", Resource)


def create(client: Client, class_id: str, name: str, image_id: str, image_user: str,
           webview_links: Union[List[WebviewLink], UNDEFINED_TYPE] = UNDEFINED, post_launch_script: Union[str, UNDEFINED_TYPE] = UNDEFINED,
           userdata: Union[str, UNDEFINED_TYPE] = UNDEFINED, ec2_region: Union[str, UNDEFINED_TYPE] = UNDEFINED,
           instance_type: Union[str, UNDEFINED_TYPE] = UNDEFINED) -> Resource:
    data = {
        'name': name,
        'image_id': image_id,
        'image_user': image_user
    }
    if webview_links is not UNDEFINED:
        data['webview_links'] = [w.to_dict() for w in webview_links]
    if post_launch_script is not UNDEFINED:
        data['post_launch_script'] = post_launch_script
    if userdata is not UNDEFINED:
        data['userdata'] = userdata
    if ec2_region is not UNDEFINED:
        data['ec2_region'] = ec2_region
    if instance_type is not UNDEFINED:
        data['instance_type'] = instance_type
    return client.post(f"/classes/{class_id}/resources", data, Resource)


def update(client: Client, class_id: str, resource_id: str, name: str, image_id: str, image_user: str,
           webview_links: Union[List[WebviewLink], UNDEFINED_TYPE] = UNDEFINED, post_launch_script: Union[str, UNDEFINED_TYPE] = UNDEFINED,
           userdata: Union[str, UNDEFINED_TYPE] = UNDEFINED, ec2_region: Union[str, UNDEFINED_TYPE] = UNDEFINED,
           instance_type: Union[str, UNDEFINED_TYPE] = UNDEFINED) -> Resource:
    data = {}
    if name is not UNDEFINED:
        data['name'] = name
    if image_id is not UNDEFINED:
        data['image_id'] = image_id
    if image_user is not UNDEFINED:
        data['image_user'] = image_user
    if webview_links is not UNDEFINED:
        data['webview_links'] = [w.to_dict() for w in webview_links]
    if post_launch_script is not UNDEFINED:
        data['post_launch_script'] = post_launch_script
    if userdata is not UNDEFINED:
        data['userdata'] = userdata
    if ec2_region is not UNDEFINED:
        data['ec2_region'] = ec2_region
    if instance_type is not UNDEFINED:
        data['instance_type'] = instance_type
    return client.patch(f"/classes/{class_id}/resources/{resource_id}", data, Resource)


def delete(client: Client, class_id: str, resource_id: str) -> None:
    client.delete(f"/classes/{class_id}/resources/{resource_id}")
