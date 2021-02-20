# coding: utf8
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List

from ..models.classes import Class
from ..models.presentations import Presentation
from .presentations import PresentationConfig
from .resources import ResourceConfig


@dataclass
class ClassConfig:
    name: str
    id: str = None
    description: str = None
    presentations: List[PresentationConfig] = field(default_factory=list)
    resources: List[ResourceConfig] = field(default_factory=list)

    def write(self, config_path: Path) -> None:
        with config_path.open('w') as f:
            json.dump(asdict(self), f, indent=2, sort_keys=True)

    @staticmethod
    def load(config_path: Path) -> ClassConfig:
        with config_path.open() as f:
            raw_config = json.load(f)
        return ClassConfig.from_dict(raw_config)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> ClassConfig:
        d['presentations'] = [PresentationConfig.from_dict(e) for e in d['presentations']]
        d['resources'] = [ResourceConfig.from_dict(e) for e in d['resources']]
        return ClassConfig(**d)

    @staticmethod
    def from_strigo(cls: Class, presentations: List[Presentation]) -> ClassConfig:
        return ClassConfig(
            id=cls.id,
            name=cls.name,
            description=cls.description,
            presentations=[PresentationConfig.from_strigo(p) for p in presentations],
            resources=[ResourceConfig.from_strigo(r) for r in cls.resources]
        )