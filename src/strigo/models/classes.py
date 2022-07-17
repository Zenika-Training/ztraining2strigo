# coding: utf8
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List

from . import format_date, parse_date
from .presentations import Note
from .resources import Resource


@dataclass
class Owner:
    id: str
    email: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> Owner:
        return Owner(**d)


@dataclass
class Class:
    id: str
    name: str
    resources: List[Resource]
    presentation_notes: List[Note]
    created_at: datetime
    updated_at: datetime
    owner: Owner = None
    description: str = None
    presentation_filename: str = None

    @property
    def str_description(self) -> str:
        return self.description or ''

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d['created_at'] = format_date(self.created_at)
        d['updated_at'] = format_date(self.updated_at)
        return d

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> Class:
        d['owner'] = Owner.from_dict(d['owner']) if 'owner' in d and d['owner'] else None
        d['created_at'] = parse_date(d['created_at'])
        d['updated_at'] = parse_date(d['updated_at'])
        d['resources'] = [Resource.from_dict(e) for e in d['resources']]
        d['presentation_notes'] = [Note.from_dict(e) for e in d['presentation_notes']]
        return Class(**d)
