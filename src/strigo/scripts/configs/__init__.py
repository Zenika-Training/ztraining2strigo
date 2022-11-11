# coding: utf8
from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict

from ..github import retrieve_script


class ScriptType(Enum):
    INIT = 'scripts'
    WINDOWS_INIT = 'win_scripts'
    POST_LAUNCH = 'post_launch_scripts'


@dataclass
class Script():
    script_type: ScriptType
    script: str
    version: str = 'main'
    env: Dict[str, str] = field(default_factory=dict)

    @staticmethod
    def from_dict(script_type: ScriptType, d: Dict[str, Any]) -> Script:
        d['env'] = {k: (v if isinstance(v, str) else json.dumps(v, separators=(',', ':'))) for k, v in d.get('env', {}).items()}
        return Script(script_type=script_type, **d)

    def __post_init__(self):
        self.script_content = retrieve_script(self.script, self.version, self.script_type.value)

    @property
    def content(self) -> str:
        script = '\n'.join(f'{key}={json.dumps(value)}' for key, value in self.env.items())
        script += '\n' + self.script_content
        return script
