# coding: utf8
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List


@dataclass
class Error(Exception):
    type: str
    message: str
    errors: List[Dict[str: Any]] = None

    def __post_init__(self):
        super().__init__(repr(self))

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> Error:
        return Error(**d)


@dataclass
class RequestValidationError(Error):

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> RequestValidationError:
        return RequestValidationError(**d)
