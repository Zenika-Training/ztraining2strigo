# coding: utf8
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List

from . import build_object


@dataclass
class Error(Exception):
    type: str
    message: str
    errors: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self):
        super().__init__(repr(self))

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> Error:
        return build_object(Error, d)


@dataclass
class RequestValidationError(Error):

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> RequestValidationError:
        return build_object(RequestValidationError, d)
