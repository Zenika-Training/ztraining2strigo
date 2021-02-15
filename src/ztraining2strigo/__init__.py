# coding: utf8

import argparse
import os
from getpass import getpass
from pathlib import Path

from strigo.api import classes as classes_api
from strigo.api import presentations as presentations_api
from strigo.client import Client
from strigo.configs import bootstrap_config_file
from strigo.configs.classes import ClassConfig

VERSION = '0.0.1'


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
