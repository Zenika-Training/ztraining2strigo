# coding: utf8

from pathlib import Path
from typing import Iterator, List, Union

from .configs import Script


def decorate_script(script: str, name: str, is_windows: bool) -> str:
    print_cmd = 'Write-Output' if is_windows else 'echo'
    decorated_script = f"##### Start {name}\n"
    decorated_script += f'{print_cmd} "--------- Start {name}"\n'
    decorated_script += script
    decorated_script += f'\n{print_cmd} "--------- End {name}"\n'
    decorated_script += f'##### End {name}\n'
    return decorated_script


def normalize_script(s: str):
    s = (s or '').strip()
    if s:
        s += '\n'
    return s


def get_scripts_content(scripts: List[Union[str, Script]], is_windows: bool) -> Iterator[str]:
    for script in scripts:
        if isinstance(script, Script):
            yield decorate_script(script.content, script.script, is_windows)
        elif isinstance(script, str):
            with Path(script).open() as f:
                yield decorate_script(f.read(), script, is_windows)


def unique_script(scripts: List[Union[str, Script]], is_windows: bool, is_post_launch: bool = False):
    full_script = normalize_script('\n'.join(get_scripts_content(scripts, is_windows)))
    if is_windows and full_script and not is_post_launch:
        full_script = f"<powershell>\n\n{full_script}\n</powershell>\n"
    return full_script
