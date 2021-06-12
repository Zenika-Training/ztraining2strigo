# coding: utf8
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List


def normalize_script(s: str):
    s = (s or '').strip()
    if s:
        s += '\n'
    return s


@dataclass
class WebviewLink:
    name: str
    url: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> WebviewLink:
        if '_id' in d:
            del d['_id']
        return WebviewLink(**d)


@dataclass
class Resource:
    id: str
    type: str
    name: str
    image_id: str
    image_user: str
    is_custom_image: bool = False
    webview_links: List[WebviewLink] = field(default_factory=list)
    post_launch_script: str = None
    userdata: str = None
    ec2_region: str = None
    instance_type: str = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> Resource:
        d['webview_links'] = [WebviewLink.from_dict(e) for e in d['webview_links']]
        d['post_launch_script'] = normalize_script(d['post_launch_script'])
        d['userdata'] = normalize_script(d['userdata'])
        return Resource(**d)
