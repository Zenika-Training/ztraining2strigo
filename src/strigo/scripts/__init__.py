# coding: utf8

from typing import List, Union, Iterator
from pathlib import Path

from .configs import Script


def normalize_script(s: str):
    s = (s or '').strip()
    if s:
        s += '\n'
    return s


def get_scripts_content(scripts: List[Union[str, Script]]) -> Iterator[str]:
    for script in scripts:
        if isinstance(script, Script):
            yield script.content
        elif isinstance(script, str):
            with Path(script).open() as f:
                yield f.read()


def unique_script(scripts: List[Union[str, Script]]):
    return normalize_script('\n'.join(get_scripts_content(scripts)))
