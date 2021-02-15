# coding: utf8

import argparse
import os
import sys
from getpass import getpass
from pathlib import Path
from typing import Callable, List

from strigo.api import classes as classes_api
from strigo.api import presentations as presentations_api
from strigo.api import resources as resources_api
from strigo.client import Client
from strigo.configs import bootstrap_config_file
from strigo.configs.classes import ClassConfig
from strigo.configs.presentations import PresentationConfig
from strigo.configs.resources import AWS_REGIONS, STRIGO_DEFAULT_INSTANCE_TYPES, STRIGO_DEFAULT_REGION, STRIGO_IMAGES, ResourceConfig, ResourceImageConfig
from strigo.models.resources import WebviewLink

from .notes_parser import parse_notes

VERSION = '0.0.1'


def _prompt(prompt: str, is_valid: Callable[[str], bool] = lambda _: True, choices: List[str] = None) -> str:
    choices_prompt = ''
    if choices:
        choices_prompt = f" ({', '.join(choices)})"
    while True:
        answer = input(f"{prompt}{choices_prompt}: ").strip()
        if answer and is_valid(answer) and (not choices or answer in choices):
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


def create(client: Client, args: argparse.Namespace) -> None:
    config_file = bootstrap_config_file(args.config)

    name = _prompt('Please enter Strigo class name')

    existing_classes = classes_api.search(client, name)
    if existing_classes:
        print(f"WARNING: Classes with same name already exists: {[c.id for c in existing_classes]}", file=sys.stderr)
        if not _confirm('Are you sure you want to create a new class with same name?'):
            return

    strigo_config = ClassConfig(name)

    description = input('Please enter Strigo class description (can be empty): ').strip()
    if not description:
        description = None
    strigo_config.description = description

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
                print(f"ERROR: You already created a machine with same name.", file=sys.stderr)
                return False
            return True
        resource_name = _prompt('Please enter machine name', is_valid=is_resource_name_valid)
        instance_type = _prompt('Please enter machine type', choices=STRIGO_DEFAULT_INSTANCE_TYPES)
        image = _prompt('Please enter machine image', choices=list(STRIGO_IMAGES.keys()) + ['custom'])
        if image == 'custom':
            image_id = _prompt('Please enter AMI ("ami-...")', is_valid=lambda id: id.startswith('ami-'))
            image_user = _prompt('Please enter image user')
            image_region = _prompt('Please enter image region', is_valid=lambda r: r in AWS_REGIONS)
            image = ResourceImageConfig(image_id, image_user, image_region)

        init_scripts: List[str] = []
        if _confirm('Do you want to add init scripts?'):
            while True:
                init_script = _prompt('Please enter path to an init script', is_valid=_is_valid_path)
                init_scripts.append(init_script)
                if not _confirm('Do you want to add another init script?'):
                    break

        post_launch_scripts: List[str] = []
        if _confirm('Do you want to add post launch scripts?'):
            while True:
                post_launch_script = _prompt('Please enter path to a post launch script', is_valid=_is_valid_path)
                post_launch_scripts.append(post_launch_script)
                if not _confirm('Do you want to add another post launch script?'):
                    break

        webview_links: List[WebviewLink] = []
        if _confirm('Do you want to add webview links?'):
            while True:
                def is_webview_link_name_valid(name: str) -> bool:
                    if name in (w.name for w in webview_links):
                        print(f"ERROR: You already created a webview link with same name.", file=sys.stderr)
                        return False
                    return True
                name = _prompt('Please enter webview link name', is_valid=is_webview_link_name_valid)
                url = _prompt('Please enter webview link url ("http://instance.autolab.strigo.io:XXXX")', is_valid=lambda url: url.startswith('http://instance.autolab.strigo.io:'))
                webview_links.append(WebviewLink(name, url))
                if not _confirm('Do you want to add another webview link?'):
                    break

        resource = ResourceConfig(resource_name, instance_type, image, init_scripts, post_launch_scripts, webview_links)
        resources.append(resource)
        if not _confirm('Do you want to add another machine?'):
            break

    strigo_config.resources = resources

    print("Creating Strigo class...")
    cls = classes_api.create(client, strigo_config.name, strigo_config.description)
    strigo_config.id = cls.id
    strigo_config.write(config_file)
    print(f"Config stored in '{config_file.absolute()}'")

    print("Uploading Strigo class presentation...")
    presentation = presentations_api.create(client, cls.id, presentation)
    if presentation:
        presentations_api.create_notes(client, cls.id, presentation.id, parse_notes(Path(presentation_config.notes_source)))

    print("Adding Strigo class resources...")
    for resource in resources:
        image = resource.image
        if isinstance(image, str):
            image = ResourceImageConfig(
                STRIGO_IMAGES[image]['amis'][STRIGO_DEFAULT_REGION],
                STRIGO_IMAGES[image]['user'],
                STRIGO_DEFAULT_REGION
            )
        userdata = ''
        for script in resource.init_scripts:
            with Path(script).open() as f:
                userdata += f.read() + '\n'
        post_launch_script = ''
        for script in resource.post_launch_scripts:
            with Path(script).open() as f:
                post_launch_script += f.read() + '\n'
        resources_api.create(client, cls.id, resource.name, image.image_id, image.image_user, resource.webview_links, post_launch_script, userdata, image.ec2_region, resource.instance_type)

    print("Done!")


def retrieve(client: Client, args: argparse.Namespace) -> None:
    config_file = bootstrap_config_file(args.config)
    cls = classes_api.get(client, args.class_id)
    presentations = presentations_api.list(client, cls.id)
    strigo_config = ClassConfig.from_strigo(cls, presentations)
    strigo_config.write(config_file)

    print(f"Config from Strigo stored in '{config_file.absolute()}'")


def main() -> None:
    parser = argparse.ArgumentParser('ztraining2strigo')
    parser.add_argument('--config', default='strigo.json', type=Path)
    subparsers = parser.add_subparsers(required=True, help='sub-command help', metavar='COMMAND')

    parser_create = subparsers.add_parser('create', help='Create config for new Strigo class. The class parameters are asked interactively.')
    parser_create.set_defaults(func=create)

    parser_retrieve = subparsers.add_parser('retrieve', help='Retrieve config from existing Strigo class')
    parser_retrieve.add_argument('class_id', metavar='CLASS_ID', type=str, help='Existing Strigo class ID')
    parser_retrieve.set_defaults(func=retrieve)

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
        print(e, file=sys.stderr)
        exit(1)
