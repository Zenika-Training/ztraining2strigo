# coding: utf8
from __future__ import annotations

from dataclasses import fields
from datetime import datetime, timezone
from functools import cache
from typing import Any, Dict, Set


def format_date(d: datetime) -> str:
    return d.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')


def parse_date(d: str) -> datetime:
    return datetime.fromisoformat(d.replace('Z', '+00:00'))


@cache
def _field_names(cls: Any) -> Set[str]:
    return {f.name for f in fields(cls)}


def build_object(cls: Any, d: Dict[str, Any]) -> object:
    return cls(**{k: v for k, v in d.items() if k in _field_names(cls)})
