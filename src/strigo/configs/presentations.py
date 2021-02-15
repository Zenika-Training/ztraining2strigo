# coding: utf8
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..models.presentations import Presentation


@dataclass
class PresentationConfig:
    file: str
    notes_source: str = 'Slides/slides.json'

    @staticmethod
    def from_strigo(presentation: Presentation) -> PresentationConfig:
        return PresentationConfig(search_file(presentation.filename))


def search_file(filename: str) -> str:
    paths = list(Path('.').glob(f"**/{filename}"))
    if len(paths) == 0:
        path = Path('PDF') / filename
    else:
        path = paths[0]
    return path.as_posix()
