# coding: utf8
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

from ..models.resources import STRIGO_DEFAULT_REGION, Resource, ViewInterface, WebviewLink
from ..scripts import unique_script
from ..scripts.configs import Script
from . import get_scripts_folder

STRIGO_DEFAULT_INSTANCE_TYPES = [
    't3.medium', 't3.large', 't3.xlarge',
    't3a.micro', 't3a.small', 't3a.medium', 't3a.large', 't3a.xlarge'
]
AWS_REGIONS = [
    'us-east-2', 'us-east-1', 'us-west-1', 'us-west-2',
    'af-south-1', 'ap-east-1', 'ap-south-1',
    'ap-northeast-1', 'ap-northeast-2', 'ap-northeast-3',
    'ap-southeast-1', 'ap-southeast-2', 'ca-central-1',
    'cn-north-1', 'cn-northwest-1',
    'eu-central-1', 'eu-west-1', 'eu-west-2', 'eu-west-3',
    'eu-south-1', 'eu-north-1', 'me-south-1', 'sa-east-1'
]


@dataclass
class ImageAWSConfig:
    user: str
    amis: Dict[str, str]

    @property
    def strigo_default_region(self):
        return STRIGO_DEFAULT_REGION

    @property
    def strigo_default_ami(self):
        return self.amis[self.strigo_default_region]


STRIGO_IMAGES = {
    'debian-8.7': ImageAWSConfig(
        user='admin',
        amis={
            STRIGO_DEFAULT_REGION: 'ami-061026464372bc7bf'
        }
    ),
    'debian-11': ImageAWSConfig(
        user='admin',
        amis={
            STRIGO_DEFAULT_REGION: 'ami-010716a347cc5be84'
        }
    ),
    'ubuntu-16.04.2': ImageAWSConfig(
        user='ubuntu',
        amis={
            STRIGO_DEFAULT_REGION: 'ami-064be016683d0de06'
        }
    ),
    'ubuntu-20.04': ImageAWSConfig(
        user='ubuntu',
        amis={
            STRIGO_DEFAULT_REGION: 'ami-0754c1bf35f85d01f',
            'eu-west-3': 'ami-077e7b9090435f0bd'
        }
    ),
    'ubuntu-22.04': ImageAWSConfig(
        user='ubuntu',
        amis={
            STRIGO_DEFAULT_REGION: 'ami-06fd571d4b092ea39'
        }
    ),
    'amazon-linux-v2.0.20221210.1': ImageAWSConfig(
        user='ec2-user',
        amis={
            STRIGO_DEFAULT_REGION: 'ami-0455da2bdc38b251e'
        }
    ),
    'centos-7.9': ImageAWSConfig(
        user='centos',
        amis={
            STRIGO_DEFAULT_REGION: 'ami-06d5af736376c3798'
        }
    ),
    'docker-17.09.0-ce': ImageAWSConfig(
        user='ubuntu',
        amis={
            STRIGO_DEFAULT_REGION: 'ami-0d601c1d4166c5e45'
        }
    ),
    'windows-server-2016': ImageAWSConfig(
        user='Administrator',
        amis={
            STRIGO_DEFAULT_REGION: 'ami-0afcd9cce919e7a9c'
        }
    ),
    'windows-server-2019': ImageAWSConfig(
        user='Administrator',
        amis={
            STRIGO_DEFAULT_REGION: 'ami-090d5efe85c2be3d1'
        }
    )
}
AMIS_TO_OS = {v.strigo_default_ami: k for k, v in STRIGO_IMAGES.items()}


@dataclass
class ResourceImageConfig:
    @property
    def id(self) -> str:
        raise NotImplementedError

    @property
    def user(self) -> str:
        raise NotImplementedError

    @property
    def region(self) -> Optional[str]:
        raise NotImplementedError

    @property
    def region_mapping(self) -> Optional[Dict[str, str]]:
        raise NotImplementedError

    @property
    def is_windows(self) -> bool:
        raise NotImplementedError

    @staticmethod
    def new(value: Union[str, Dict[str, Any]]) -> ResourceImageConfig:
        image_name = None
        if isinstance(value, str):
            image_name = value
        elif isinstance(value, dict):
            if 'image_name' in value:
                image_name = value['image_name']
            elif 'image_id' in value:
                return FullResourceImageConfig.from_dict(value)
        if image_name:
            if image_name not in STRIGO_IMAGES:
                raise ValueError(
                    f"Unknown image name: {image_name}\n"
                    f"Available image names are: {', '.join(STRIGO_IMAGES.keys())}\n"
                    f"Or use a custom image with '{{image_id: {image_name}, image_user: <image_user>, ec2_region: <ec2_region>}}'"
                )
            return PredefinedResourceImageConfig(image_name)

        raise NotImplementedError()

    @staticmethod
    def from_strigo(is_custom_image: bool, image_id: str, image_user: str, ec2_region: Union[str, None], image_region_mapping: Union[Dict[str, str], None]) -> ResourceImageConfig:
        if not is_custom_image and image_id in AMIS_TO_OS:
            return PredefinedResourceImageConfig(AMIS_TO_OS[image_id])
        else:
            return FullResourceImageConfig(image_id, image_user, ec2_region, image_region_mapping)


@dataclass
class PredefinedResourceImageConfig(ResourceImageConfig):
    image_name: str

    @property
    def id(self) -> str:
        return STRIGO_IMAGES[self.image_name].strigo_default_ami

    @property
    def user(self) -> str:
        return STRIGO_IMAGES[self.image_name].user

    @property
    def region(self) -> Optional[str]:
        return STRIGO_IMAGES[self.image_name].strigo_default_region

    @property
    def region_mapping(self) -> Optional[Dict[str, str]]:
        return STRIGO_IMAGES[self.image_name].amis

    @property
    def is_windows(self) -> bool:
        return self.image_name.startswith('windows')


@dataclass
class FullResourceImageConfig(ResourceImageConfig):
    image_id: str
    image_user: str
    ec2_region: Optional[str] = None
    image_region_mapping: Optional[Dict[str, str]] = field(default_factory=dict)

    @property
    def id(self) -> str:
        return self.image_id

    @property
    def user(self) -> str:
        return self.image_user

    @property
    def region(self) -> Optional[str]:
        return self.ec2_region

    @property
    def region_mapping(self) -> Optional[Dict[str, str]]:
        return self.image_region_mapping

    @property
    def is_windows(self) -> bool:
        return False

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> FullResourceImageConfig:
        d['image_region_mapping'] = d.get('image_region_mapping', {})
        d['image_region_mapping'][d['ec2_region']] = d['image_id']
        return FullResourceImageConfig(**d)


@dataclass
class ResourceConfig:
    name: str
    instance_type: str
    image: ResourceImageConfig
    is_windows: bool = False
    init_scripts: List[Script] = field(default_factory=list)
    post_launch_scripts: List[Script] = field(default_factory=list)
    view_interface: Optional[ViewInterface] = None
    webview_links: List[WebviewLink] = field(default_factory=list)

    def unique_init_script(self):
        return unique_script(self.init_scripts, self.is_windows)

    def unique_post_launch_script(self):
        return unique_script(self.post_launch_scripts, self.is_windows, True)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> ResourceConfig:
        d['image'] = ResourceImageConfig.new(d['image'])
        if 'is_windows' not in d:
            d['is_windows'] = d['image'].is_windows
        init_scripts = []
        for init_script in d['init_scripts']:
            init_scripts.append(Script.new_init_script(init_script, d['is_windows']))
        d['init_scripts'] = init_scripts
        post_launch_scripts = []
        for post_launch_script in d['post_launch_scripts']:
            post_launch_scripts.append(Script.new_post_launch_script(post_launch_script))
        d['post_launch_scripts'] = post_launch_scripts
        d['view_interface'] = ViewInterface(d['view_interface']) if 'view_interface' in d and d['view_interface'] else None
        d['webview_links'] = [WebviewLink.from_dict(e) for e in d['webview_links']]
        return ResourceConfig(**d)

    @staticmethod
    def from_strigo(resource: Resource) -> ResourceConfig:
        image = ResourceImageConfig.from_strigo(resource.is_custom_image, resource.image_id, resource.image_user, resource.ec2_region, resource.image_region_mapping)
        scripts_folder = get_scripts_folder()
        normalized_resource_name = resource.name.replace('\\s', '_')
        init_scripts: List[Script] = []
        if resource.userdata:
            script_path = scripts_folder / f"init_{normalized_resource_name}.{'ps1' if image.is_windows else 'sh'}"
            with script_path.open('wt') as f:
                f.write(resource.userdata.replace('<powershell>', '').replace('</powershell>', '').strip() + '\n')
            init_scripts.append(Script.new_init_script(script_path.as_posix(), image.is_windows))
        post_launch_scripts: List[Script] = []
        if resource.post_launch_script:
            script_path = scripts_folder / f"post_launch_{normalized_resource_name}.ps1"
            with script_path.open('wt') as f:
                f.write(resource.post_launch_script)
            post_launch_scripts.append(Script.new_post_launch_script(script_path.as_posix()))
        return ResourceConfig(
            name=resource.name,
            instance_type=resource.instance_type,
            image=image,
            is_windows=image.is_windows,
            view_interface=resource.view_interface,
            webview_links=resource.webview_links,
            init_scripts=init_scripts,
            post_launch_scripts=post_launch_scripts
        )
