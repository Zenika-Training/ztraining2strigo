# coding: utf8

import re
from typing import Iterator, List

from .configs import Script

SCRIPT_COMMENT_RE = re.compile(r'^[ \t]?#[^!].*\n', re.MULTILINE)
MULTIPLE_EMPTY_LINES_RE = re.compile(r'^\n\n+', re.MULTILINE)


def decorate_script(script: str, name: str, is_windows: bool) -> str:
    print_cmd = 'Write-Output' if is_windows else 'echo'
    decorated_script = f'{print_cmd} "--------- Start {name}"\n'
    decorated_script += script
    decorated_script += f'\n{print_cmd} "--------- End {name}"\n'
    return decorated_script


def normalize_script(s: str):
    s = (s or '').strip()
    if s:
        s += '\n'
    return s


def get_scripts_content(scripts: List[Script], is_windows: bool) -> Iterator[str]:
    for script in scripts:
        yield decorate_script(script.content, script.name, is_windows)


def minify_script(script: str) -> str:
    script = SCRIPT_COMMENT_RE.sub('', script)
    script = MULTIPLE_EMPTY_LINES_RE.sub('\n', script)
    return script


def unique_script(scripts: List[Script], is_windows: bool, is_post_launch: bool = False):
    full_script = normalize_script('\n'.join(get_scripts_content(scripts, is_windows)))
    if is_windows and full_script and not is_post_launch:
        full_script = f"<powershell>\n\n{full_script}\n</powershell>\n"
    elif not is_windows and full_script:
        full_script = f"#!/bin/bash\n\n{full_script}"
    full_script = minify_script(full_script)
    return full_script
