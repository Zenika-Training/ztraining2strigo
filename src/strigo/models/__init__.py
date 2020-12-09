# coding: utf8
from __future__ import annotations

from datetime import datetime, timezone


def format_date(d: datetime) -> str:
    return d.astimezone(timezone.UTC).isoformat().replace('+00:00', 'Z')


def parse_date(d: str) -> datetime:
    return datetime.fromisoformat(d.replace('Z', '+00:00'))
