# coding: utf8
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List

from . import format_date, parse_date


@dataclass
class Note:
    page: int
    content: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> Note:
        return Note(**d)


@dataclass
class Presentation:
    id: str
    class_id: str
    md5: str
    upload_date: datetime
    size_bytes: int
    filename: str
    content_type: List[str]

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d['upload_date'] = format_date(self.upload_date)
        return d

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> Presentation:
        d['upload_date'] = parse_date(d['upload_date'])
        return Presentation(**d)
