# coding: utf8
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from ..scripts import normalize_script
from . import build_object


class ViewInterface(str, Enum):
    TERMINAL = 'terminal'
    DESKTOP = 'desktop'


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
        return build_object(WebviewLink, d)


@dataclass
class Resource:
    id: str
    type: str
    name: str
    image_id: str
    image_user: str
    is_custom_image: bool = False
    view_interface: Optional[ViewInterface] = None
    webview_links: List[WebviewLink] = field(default_factory=list)
    post_launch_script: Optional[str] = None
    userdata: Optional[str] = None
    ec2_region: Optional[str] = None
    instance_type: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> Resource:
        d['view_interface'] = ViewInterface(d['view_interface']) if 'view_interface' in d else None
        if d['is_custom_image']:
            if 'image_id' not in d:  # Web based lab (not yet used in ztraining2strigo but has to be handled)
                d['image_id'] = ''
            if 'image_user' not in d:
                d['image_user'] = ''
        d['webview_links'] = [WebviewLink.from_dict(e) for e in d['webview_links']]
        d['post_launch_script'] = normalize_script(d.get('post_launch_script', None))
        d['userdata'] = normalize_script(d.get('userdata', None))
        return build_object(Resource, d)
