# coding: utf8

import argparse
import os
import sys
from difflib import unified_diff
from getpass import getpass
from itertools import zip_longest
from pathlib import Path
from typing import Any, Callable, Dict, List

from strigo.api import UNDEFINED
from strigo.api import classes as classes_api
from strigo.api import presentations as presentations_api
from strigo.api import resources as resources_api
from strigo.client import Client
from strigo.configs import bootstrap_config_file
from strigo.configs.classes import ClassConfig
from strigo.configs.presentations import PresentationConfig
from strigo.configs.resources import AWS_REGIONS, STRIGO_DEFAULT_INSTANCE_TYPES, STRIGO_IMAGES, FullResourceImageConfig, PredefinedResourceImageConfig, ResourceConfig, ResourceImageConfig
from strigo.models.classes import Class
from strigo.models.resources import Resource, ViewInterface, WebviewLink
from strigo.scripts.configs import Script

from .notes_parser import parse_notes

VERSION = '0.1.0'


def _prompt(prompt: str, is_valid: Callable[[str], bool] = lambda a: a, choices: List[str] = None) -> str:
    choices_prompt = ''
    if choices:
        choices_prompt = f" ({', '.join(choices)})"
    while True:
        answer = input(f"{prompt}{choices_prompt}: ").strip()
        if is_valid(answer) and (not choices or answer in choices):
            break
        else:
            print('Invalid value, try again.', file=sys.stderr)
    return answer


def _is_valid_path(path: str) -> bool:
    if Path(path).exists():
        return True
    else:
        print(f"ERROR: File {path} does not exists.", file=sys.stderr)
        return False


def _confirm(prompt: str) -> bool:
    while True:
        answer = input(f"{prompt} [y/N] ")
        if answer.lower() in ['y', 'yes']:
            return True
        elif answer.lower() in ['', 'n', 'no']:
            return False
        else:
            print('Please answer by y[es] or n[o]', file=sys.stderr)


def _show_diff(a: str, b: str, prefix: str = '\t') -> None:
    diff_lines = unified_diff(
        [] if not a else a.splitlines(keepends=True),
        [] if not b else b.splitlines(keepends=True),
        fromfile='strigo', tofile='local'
    )
    sys.stdout.writelines(prefix + line for line in diff_lines)


def _dict_to_display(d: Dict[str, Any]) -> str:
    return '\n'.join(sorted(f"{k}: {v}" for k, v in d.items())) + '\n'


def _to_strigo(client: Client, config: ClassConfig, existing_class: Class = None, dry_run: bool = False, diff: bool = False) -> None:
    messages_prefix = ''
    if dry_run:
        messages_prefix = '(dry-run) '

    if not existing_class:
        existing_class = classes_api.get(client, config.id)

    needs_update = False
    if config.name != existing_class.name:
        print(f"Will update class name from {existing_class.name} to {config.name}")
        needs_update = True
    if config.strigo_description and config.strigo_description != existing_class.str_description:
        print("Will update class description")
        _show_diff(existing_class.str_description + '\n', config.strigo_description + '\n')
        needs_update = True
    if config.labels and set(config.labels) != set(existing_class.labels):
        print("Will update class labels")
        _show_diff('\n'.join(sorted(existing_class.labels)) + '\n', '\n'.join(sorted(config.labels)) + '\n')
        needs_update = True
    if needs_update and not dry_run:
        print(f"{messages_prefix}Updating class {existing_class.id}")
        classes_api.update(client, existing_class.id, config.name, config.strigo_description or UNDEFINED, config.labels or UNDEFINED)

    existing_presentations = presentations_api.list(client, existing_class.id)
    existing_presentations_per_filename = {p.filename: p for p in existing_presentations}
    presentations_per_filename = {Path(p.file).name: p for p in config.presentations}
    for presentation in (p for p in existing_presentations if p.filename not in presentations_per_filename):
        print(f"{messages_prefix}Deleting existing presentation with id {presentation.id} of file {presentation.filename}")
        if not dry_run:
            presentations_api.delete(client, existing_class.id, presentation.id)
    for presentation in (p for f, p in presentations_per_filename.items() if f not in existing_presentations_per_filename):
        print(f"{messages_prefix}Creating presentation {presentation.file}")
        if not dry_run:
            created_presentation = presentations_api.create(client, existing_class.id, Path(presentation.file))
            presentations_api.create_notes(client, existing_class.id, created_presentation.id, parse_notes(Path(presentation.notes_source)))
    for presentation, existing_presentation in ((p, existing_presentations_per_filename[f]) for f, p in presentations_per_filename.items() if f in existing_presentations_per_filename):
        notes = parse_notes(Path(presentation.notes_source))
        needs_update = presentation.file_size() != existing_presentation.size_bytes
        if not needs_update:  # Don't verify checksum if update is already needed
            needs_update = presentation.file_md5_sum() != existing_presentation.md5
        if needs_update:
            print(f"{messages_prefix}Updating presentation {presentation.file}")
            if not dry_run:
                updated_presentation = presentations_api.update(client, existing_class.id, existing_presentation.id, Path(presentation.file))
                presentations_api.create_notes(client, existing_class.id, updated_presentation.id, notes)
        else:
            existing_notes = presentations_api.get_notes(client, existing_class.id, existing_presentation.id)
            if notes != existing_notes:
                print(f"{messages_prefix}Updating presentation notes for {presentation.file}")
                if not dry_run:
                    presentations_api.create_notes(client, existing_class.id, existing_presentation.id, notes)

    existing_resources = resources_api.list(client, existing_class.id)
    for index, (resource, existing_resource) in enumerate(zip_longest(config.resources, existing_resources)):
        resource: ResourceConfig
        existing_resource: Resource
        if resource is None:
            print(f"{messages_prefix}Deleting machine {index} named {existing_resource.name}")
            if not dry_run:
                resources_api.delete(client, existing_class.id, existing_resource.id)
        else:
            image = resource.image

            init_script = resource.unique_init_script() or UNDEFINED
            post_launch_script = resource.unique_post_launch_script() or UNDEFINED

            if existing_resource is None:
                print(f"{messages_prefix}Creating machine {index} named {resource.name}")
                if not dry_run:
                    resources_api.create(
                        client, existing_class.id, resource.name, image.id, image.user,
                        resource.view_interface, resource.webview_links,
                        post_launch_script, init_script,
                        image.region, resource.instance_type,
                        image.region_mapping
                    )
            else:
                needs_update = False

                if resource.name != existing_resource.name:
                    print(f"Will update machine {index} name from {existing_resource.name} to {resource.name}")
                    needs_update = True
                if resource.instance_type != existing_resource.instance_type:
                    print(f"Will update machine {index} type from {existing_resource.instance_type} to {resource.instance_type}")
                    needs_update = True
                if image.region_mapping != existing_resource.image_region_mapping:
                    print(f"Will update machine {index} images")
                    if diff:
                        _show_diff(_dict_to_display(existing_resource.image_region_mapping), _dict_to_display(image.region_mapping))
                    needs_update = True
                if image.user != existing_resource.image_user:
                    print(f"Will update machine {index} image user from {existing_resource.image_user} to {image.user}")
                    needs_update = True
                if init_script != existing_resource.userdata and (init_script or existing_resource.userdata):
                    print(f"Will update machine {index} init script")
                    if diff:
                        _show_diff(existing_resource.userdata, init_script)
                    needs_update = True
                if post_launch_script != existing_resource.post_launch_script and (post_launch_script or existing_resource.post_launch_script):
                    print(f"Will update machine {index} post launch script")
                    if diff:
                        _show_diff(existing_resource.post_launch_script, post_launch_script)
                    needs_update = True
                if resource.view_interface is not None and resource.view_interface != existing_resource.view_interface:
                    print(f"Will update machine {index} view interface from {existing_resource.view_interface.value} to {resource.view_interface.value}")
                    needs_update = True
                if resource.webview_links != existing_resource.webview_links:
                    print(f"Will update machine {index} webview links")
                    needs_update = True
                if needs_update:
                    print(f"{messages_prefix}Updating machine {index} named {resource.name}")
                    if not dry_run:
                        resources_api.update(
                            client, existing_class.id, existing_resource.id,
                            resource.name, image.id, image.user,
                            resource.view_interface, resource.webview_links,
                            post_launch_script, init_script,
                            image.region, resource.instance_type,
                            image.region_mapping
                        )


def create(client: Client, args: argparse.Namespace) -> None:
    config_file = bootstrap_config_file(args.config)

    name = _prompt('Please enter Strigo class name')

    existing_classes = classes_api.search(client, name)
    if existing_classes:
        print(f"WARNING: Classes with same name already exists: {[c.id for c in existing_classes]}", file=sys.stderr)
        if not _confirm('Are you sure you want to create a new class with same name?'):
            return

    strigo_config = ClassConfig(name)

    print('Please enter Strigo class description (can be empty, can be multiline, Ctrl-D or Ctrl-Z (windows) to validate):')
    while True:
        try:
            line = input().strip()
            strigo_config.description.append(line)
        except EOFError:
            break

    labels = _prompt('Please enter Strigo class labels (comma-separated list, can be empty)', is_valid=lambda _: True)
    strigo_config.labels = [l.strip() for l in labels.split(',') if l]

    presentation = _prompt(
        'Please enter path to presentation file (typically "pdf/Zenika-Formation-xxx-Slides.pdf" or "pdf/Zenika-training-material-Slides.pdf")',
        is_valid=_is_valid_path
    )
    presentation = Path(presentation)

    presentation_config = PresentationConfig(presentation.as_posix())
    strigo_config.presentations.append(presentation_config)

    resources: List[ResourceConfig] = []
    while True:
        def is_resource_name_valid(name: str) -> bool:
            if name in (r.name for r in resources):
                print("ERROR: You already created a machine with same name.", file=sys.stderr)
                return False
            return True
        resource_name = _prompt('Please enter machine name', is_valid=is_resource_name_valid)
        instance_type = _prompt('Please enter machine type', choices=STRIGO_DEFAULT_INSTANCE_TYPES)
        image_name = _prompt('Please enter machine image', choices=list(STRIGO_IMAGES.keys()) + ['custom'])
        view_interface = None
        if image_name == 'custom':
            image_id = _prompt('Please enter AMI ("ami-...")', is_valid=lambda id: id.startswith('ami-'))
            image_user = _prompt('Please enter image user')
            image_region = _prompt('Please enter image region', is_valid=lambda r: r in AWS_REGIONS)
            image: ResourceImageConfig = FullResourceImageConfig(image_id, image_user, image_region)
            view_interface = _prompt('Please enter machine view interface', choices=[e.value for e in ViewInterface])
        else:
            image = PredefinedResourceImageConfig(image_name)

        init_scripts: List[Script] = []
        if _confirm('Do you want to add init scripts?'):
            while True:
                init_script = _prompt('Please enter path to an init script', is_valid=_is_valid_path)
                init_scripts.append(Script.new_init_script(init_script, image.is_windows))
                if not _confirm('Do you want to add another init script?'):
                    break

        post_launch_scripts: List[Script] = []
        if _confirm('Do you want to add post launch scripts?'):
            while True:
                post_launch_script = _prompt('Please enter path to a post launch script', is_valid=_is_valid_path)
                post_launch_scripts.append(Script.new_post_launch_script(post_launch_script))
                if not _confirm('Do you want to add another post launch script?'):
                    break

        webview_links: List[WebviewLink] = []
        if _confirm('Do you want to add webview links?'):
            while True:
                def is_webview_link_name_valid(name: str) -> bool:
                    if name in (w.name for w in webview_links):
                        print("ERROR: You already created a webview link with same name.", file=sys.stderr)
                        return False
                    return True
                name = _prompt('Please enter webview link name', is_valid=is_webview_link_name_valid)
                url = _prompt('Please enter webview link url ("http://instance.autolab.strigo.io:XXXX")', is_valid=lambda url: url.startswith('http://instance.autolab.strigo.io:'))
                webview_links.append(WebviewLink(name, url))
                if not _confirm('Do you want to add another webview link?'):
                    break

        resource = ResourceConfig(resource_name, instance_type, image, image.is_windows, init_scripts, post_launch_scripts, view_interface, webview_links)
        resources.append(resource)
        if not _confirm('Do you want to add another machine?'):
            break

    strigo_config.resources = resources

    print("Creating Strigo class...")
    cls = classes_api.create(client, strigo_config.name, strigo_config.strigo_description or UNDEFINED, strigo_config.labels or UNDEFINED)
    strigo_config.id = cls.id
    strigo_config.write(config_file)
    print(f"Config stored in '{config_file.absolute()}'")

    _to_strigo(client, strigo_config, existing_class=cls)
    print("Done!")


def retrieve(client: Client, args: argparse.Namespace) -> None:
    config_file = bootstrap_config_file(args.config)
    cls = classes_api.get(client, args.class_id)
    presentations = presentations_api.list(client, cls.id)
    strigo_config = ClassConfig.from_strigo(cls, presentations)
    strigo_config.write(config_file)

    print(f"Config from Strigo stored in '{config_file.absolute()}'")


def update(client: Client, args: argparse.Namespace) -> None:
    config_path: Path = args.config
    if not config_path.exists():
        toml_config_path = config_path.with_suffix('.toml')
        if config_path.as_posix() == 'strigo.json' and toml_config_path.exists():
            config_path = toml_config_path
        else:
            print(f"ERROR: Config file {config_path} does not exists.", file=sys.stderr)
            exit(1)

    strigo_config = ClassConfig.load(config_path)
    _to_strigo(client, strigo_config, dry_run=args.dry_run, diff=args.diff)


def main() -> None:
    parser = argparse.ArgumentParser('ztraining2strigo')
    parser.add_argument('--config', default='strigo.json', type=Path)
    subparsers = parser.add_subparsers(required=True, help='sub-command help', metavar='COMMAND')

    parser_create = subparsers.add_parser('create', help='Create config for new Strigo class. The class parameters are asked interactively.')
    parser_create.set_defaults(func=create)

    parser_retrieve = subparsers.add_parser('retrieve', help='Retrieve config from existing Strigo class')
    parser_retrieve.add_argument('class_id', metavar='CLASS_ID', type=str, help='Existing Strigo class ID')
    parser_retrieve.set_defaults(func=retrieve)

    parser_update = subparsers.add_parser('update', help='Update Strigo class from config')
    parser_update.add_argument('--dry-run', '-n', action='store_true', help='Do not perform update')
    parser_update.add_argument('--diff', '-d', action='store_true', help='Display diff of changes to apply in machines scripts')
    parser_update.set_defaults(func=update)

    args = parser.parse_args()

    strigo_org_id = os.environ.get('STRIGO_ORG_ID', None)
    strigo_api_key = os.environ.get('STRIGO_API_KEY', None)
    if strigo_org_id is None or strigo_api_key is None:
        print("Environnement variables 'STRIGO_ORG_ID' or 'STRIGO_API_KEY' for Strigo authentication are not set")
        if strigo_org_id is None:
            strigo_org_id = input('Please enter Strigo Organization ID: ')
        if strigo_api_key is None:
            strigo_api_key = getpass('Please enter Strigo API key: ')
    client = Client(strigo_org_id, strigo_api_key)

    try:
        args.func(client, args)
    except Exception as e:
        import traceback
        traceback.print_exc(limit=None if os.environ.get('DEBUG', False) else 0)
        exit(1)
