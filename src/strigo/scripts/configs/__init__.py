# coding: utf8
from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Union

from ..github import retrieve_script


class ScriptType(Enum):
    INIT = 'scripts'
    WINDOWS_INIT = 'win_scripts'
    POST_LAUNCH = 'post_launch_scripts'


class Script:
    @property
    def name(self) -> str:
        raise NotImplementedError

    @property
    def content(self) -> str:
        raise NotImplementedError

    @staticmethod
    def _new_script(script_type: ScriptType, d: Dict[str, Any]) -> Script:
        if 'path' in d:
            return LocalScript.from_dict(d)
        elif 'script' in d:
            return RemoteScript.from_dict(script_type, d)
        raise NotImplementedError()

    @staticmethod
    def new_init_script(value: Union[str, Dict[str, Any]], is_windows: bool) -> Script:
        if isinstance(value, str):
            return LocalScript(value)
        elif isinstance(value, dict):
            script_type = ScriptType.WINDOWS_INIT if is_windows else ScriptType.INIT
            return Script._new_script(script_type, value)

    @staticmethod
    def new_post_launch_script(value: Union[str, Dict[str, Any]]) -> Script:
        if isinstance(value, str):
            return LocalScript(value)
        elif isinstance(value, dict):
            return Script._new_script(ScriptType.POST_LAUNCH, value)


@dataclass
class LocalScript(Script):
    path: str

    @property
    def name(self) -> str:
        return self.path

    @property
    def content(self) -> str:
        with Path(self.path).open() as f:
            return f.read()

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> Script:
        return LocalScript(**d)


@dataclass
class RemoteScript(Script):
    script_type: ScriptType  # For the folder in GitHub repository
    script: str
    version: str = 'main'
    env: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        self.script_content = retrieve_script(self.script, self.version, self.script_type.value)

    @property
    def name(self) -> str:
        return self.script

    @property
    def content(self) -> str:
        script = '\n'.join(f'{key}={json.dumps(value)}' for key, value in self.env.items())
        script += '\n' + self.script_content
        return script

    @staticmethod
    def from_dict(script_type: ScriptType, d: Dict[str, Any]) -> Script:
        d['env'] = {k: (v if isinstance(v, str) else json.dumps(v, separators=(',', ':'))) for k, v in d.get('env', {}).items()}
        return RemoteScript(script_type=script_type, **d)
