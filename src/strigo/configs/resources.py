# coding: utf8
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Union

from ..models.resources import Resource, WebviewLink
from ..scripts import unique_script
from ..scripts.configs import Script, ScriptType
from . import get_scripts_folder

STRIGO_DEFAULT_INSTANCE_TYPES = ['t3.medium', 't3.large', 't3.xlarge']
AWS_REGIONS = [
    'us-east-2', 'us-east-1', 'us-west-1', 'us-west-2',
    'af-south-1', 'ap-east-1', 'ap-south-1',
    'ap-northeast-1', 'ap-northeast-2', 'ap-northeast-3',
    'ap-southeast-1', 'ap-southeast-2', 'ca-central-1',
    'cn-north-1', 'cn-northwest-1',
    'eu-central-1', 'eu-west-1', 'eu-west-2', 'eu-west-3',
    'eu-south-1', 'eu-north-1', 'me-south-1', 'sa-east-1'
]
STRIGO_DEFAULT_REGION = 'eu-central-1'
STRIGO_IMAGES = {
  'debian-8.7': {
    'user': 'admin',
    'amis': {
      STRIGO_DEFAULT_REGION: 'ami-5900cc36'
    }
  },
  'fedora-26': {
    'user': 'fedora',
    'amis': {
      STRIGO_DEFAULT_REGION: 'ami-5364c43c'
    }
  },
  'ubuntu-14.04.5': {
    'user': 'ubuntu',
    'amis': {
      STRIGO_DEFAULT_REGION: 'ami-e6de6a89'
    }
  },
  'ubuntu-16.04.2': {
    'user': 'ubuntu',
    'amis': {
      STRIGO_DEFAULT_REGION: 'ami-1e339e71'
    }
  },
  'ubuntu-20.04': {
    'user': 'ubuntu',
    'amis': {
      STRIGO_DEFAULT_REGION: 'ami-0feb4583c4b758dea'
    }
  },
  'amazon-linux-2017.09.1': {
    'user': 'ec2-user',
    'amis': {
      STRIGO_DEFAULT_REGION: 'ami-ac442ac3'
    }
  },
  'amazon-linux-v2-2017.09.1': {
    'user': 'ec2-user',
    'amis': {
      STRIGO_DEFAULT_REGION: 'ami-1b2bb774'
    }
  },
  'centos-7': {
    'user': 'centos',
    'amis': {
      STRIGO_DEFAULT_REGION: 'ami-337be65c'
    }
  },
  'docker-17.09.0-ce': {
    'user': 'ubuntu',
    'amis': {
      STRIGO_DEFAULT_REGION: 'ami-614dcd0e'
    }
  },
  'windows-server-2016': {
    'user': 'Administrator',
    'amis': {
      STRIGO_DEFAULT_REGION: 'ami-0ea21e760f354e854'
    }
  }
}
AMIS_TO_OS = {v['amis'][STRIGO_DEFAULT_REGION]: k for k, v in STRIGO_IMAGES.items()}


@dataclass
class ResourceImageConfig:
    image_id: str
    image_user: str
    ec2_region: str = None

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> ResourceImageConfig:
        return ResourceImageConfig(**d)

    @staticmethod
    def from_image_name(image_name: str) -> ResourceImageConfig:
        if image_name not in STRIGO_IMAGES:
            raise ValueError("\n".join([
                f"Unknown image name: {image_name}",
                f"Available image names are: {', '.join(STRIGO_IMAGES.keys())}",
                f"Or use a custom image with '{{image_id: {image_name}, image_user: <image_user>, ec2_region: <ec2_region>}}'"
            ]))
        image_id = STRIGO_IMAGES[image_name]['amis'][STRIGO_DEFAULT_REGION]
        image_user = STRIGO_IMAGES[image_name]['user']
        return ResourceImageConfig(image_id, image_user, STRIGO_DEFAULT_REGION)


@dataclass
class ResourceConfig:
    name: str
    instance_type: str
    image: Union[str, ResourceImageConfig]
    is_windows: bool = False
    init_scripts: List[Union[str, Script]] = field(default_factory=list)
    post_launch_scripts: List[str] = field(default_factory=list)
    webview_links: List[WebviewLink] = field(default_factory=list)

    def unique_init_script(self):
        init_script = unique_script(self.init_scripts)
        if self.is_windows:
            init_script = f"<powershell>\n\n{init_script}\n</powershell>\n"
        return init_script

    def unique_post_launch_script(self):
        return unique_script(self.post_launch_scripts)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> ResourceConfig:
        if not isinstance(d['image'], str):
            d['image'] = ResourceImageConfig.from_dict(d['image'])
        if 'is_windows' not in d:
            d['is_windows'] = _is_windows(d['image'])
        init_scripts = []
        for init_script in d['init_scripts']:
            if not isinstance(init_script, str):
                script_type = ScriptType.WINDOWS_INIT if d['is_windows'] else ScriptType.INIT
                init_script = Script.from_dict(script_type, init_script)
            init_scripts.append(init_script)
        d['init_scripts'] = init_scripts
        post_launch_scripts = []
        for post_launch_script in d['post_launch_scripts']:
            if not isinstance(post_launch_script, str):
                post_launch_script = Script.from_dict(ScriptType.POST_LAUNCH, post_launch_script)
            post_launch_scripts.append(post_launch_script)
        d['post_launch_scripts'] = post_launch_scripts
        d['webview_links'] = [WebviewLink.from_dict(e) for e in d['webview_links']]
        return ResourceConfig(**d)

    @staticmethod
    def from_strigo(resource: Resource) -> ResourceConfig:
        if not resource.is_custom_image:
            image = _parse_image(resource.image_id, resource.image_user, resource.ec2_region)
        else:
            image = ResourceImageConfig(resource.image_id, resource.image_user, resource.ec2_region)
        is_windows = _is_windows(image)
        scripts_folder = get_scripts_folder()
        normalized_resource_name = resource.name.replace('\\s', '_')
        init_scripts = []
        if resource.userdata:
            script_path = scripts_folder / f"init_{normalized_resource_name}.{'ps1' if is_windows else 'sh'}"
            with script_path.open('wt') as f:
                f.write(resource.userdata.replace('<powershell>', '').replace('</powershell>', '').strip() + '\n')
            init_scripts.append(script_path.as_posix())
        post_launch_scripts = []
        if resource.post_launch_script:
            script_path = scripts_folder / f"post_launch_{normalized_resource_name}.ps1"
            with script_path.open('wt') as f:
                f.write(resource.post_launch_script)
            post_launch_scripts.append(script_path.as_posix())
        return ResourceConfig(
            name=resource.name,
            instance_type=resource.instance_type,
            image=image,
            is_windows=is_windows,
            webview_links=resource.webview_links,
            init_scripts=init_scripts,
            post_launch_scripts=post_launch_scripts
        )


def _is_windows(image: Union[str, ResourceImageConfig]) -> bool:
    return isinstance(image, str) and image.startswith('windows')


def _parse_image(image_id: str, image_user: str, ec2_region: str) -> Union[str, ResourceImageConfig]:
    return AMIS_TO_OS.get(image_id, ResourceImageConfig(image_id, image_user, ec2_region))
