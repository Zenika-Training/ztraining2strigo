# coding: utf8
from __future__ import annotations

from pathlib import Path


def bootstrap_config_file(config_path: Path, check_not_exists: bool = True) -> Path:
    if check_not_exists and config_path.exists():
        raise FileExistsError(f"Config file '{config_path.absolute()}' already exists")
    else:
        config_path.parent.mkdir(parents=True, exist_ok=True)
    return config_path


def get_scripts_folder() -> Path:
    scripts_folder = Path('.') / 'Installation' / 'strigo'
    scripts_folder.mkdir(parents=True, exist_ok=True)
    return scripts_folder
