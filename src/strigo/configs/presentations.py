# coding: utf8
from __future__ import annotations

from dataclasses import dataclass
from hashlib import md5
from pathlib import Path
from typing import Any, Dict

from ..models.presentations import Presentation


@dataclass
class PresentationConfig:
    file: str
    notes_source: str = 'Slides/slides.json'

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> PresentationConfig:
        return PresentationConfig(**d)

    @staticmethod
    def from_strigo(presentation: Presentation) -> PresentationConfig:
        return PresentationConfig(search_file(presentation.filename))

    def file_size(self) -> int:
        return Path(self.file).stat().st_size

    def file_md5_sum(self) -> str:
        hasher = md5()
        with Path(self.file).open('rb') as f:
            for chunk in iter(lambda: f.read(65536), b''):
                hasher.update(chunk)
        return hasher.hexdigest()


def search_file(filename: str) -> str:
    paths = list(Path('.').glob(f"**/{filename}"))
    if len(paths) == 0:
        path = Path('PDF') / filename
    else:
        path = paths[0]
    return path.as_posix()
