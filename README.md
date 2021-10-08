# Ztraining2strigo

Create Strigo class for Zenika training.

## Install

### Windows

1. Download the `ztraining2strigo-x.y.z.exe` from latest release.
2. Rename it to `ztraining2strigo.exe`
3. Add it to your `PATH`

An alternative is to follow the procedure for [other OS](#other-os).

### Other OS

1. Make sure to have [Python](https://www.python.org/downloads/) >= 3.7 installed.
2. Download the `ztraining2strigo-x.y.z-py3-none-any.whl` from latest release.
3. Install the wheel package:

    ```shell
    pip install ztraining2strigo-x.y.z-py3-none-any.whl
    ```

### Docker

1. Get the image `zenika/ztraining2strigo:x.y.z`:

    ```shell
    docker image pull zenika/ztraining2strigo:x.y.z
    ```

2. Define an alias `ztraining2strigo`:

    ```shell
    alias ztraining2strigo='docker container run --rm --volume $(pwd):/training --user $(id -u):$(id -g) --env STRIGO_ORG_ID --env STRIGO_API_KEY --env Z2S_TRACE_HTTP --interactive --tty zenika/ztraining2strigo:x.y.z'
    ```

## Strigo authentication

1. Go to https://app.strigo.io/settings#account
2. Scroll to section "Authentication Credentials"
3. Define the environment variables:
  - `STRIGO_ORG_ID` with the value of "Organization ID"
  - `STRIGO_API_KEY` with the value of "API Key"

If the environment variables are not set, the Strigo credentials will be asked when launching the tool.

## Usage

1. Go to the root of your training
2. Launch any command of the `ztraining2strigo` binary

```shell-session
$ ztraining2strigo --help
usage: ztraining2strigo [-h] [--config CONFIG] COMMAND ...

positional arguments:
  COMMAND          sub-command help
    create         Create config for new Strigo class. The class parameters are asked interactively.
    retrieve       Retrieve config from existing Strigo class
    update         Update Strigo class from config

optional arguments:
  -h, --help       show this help message and exit
  --config CONFIG
```

### Retrieve configuration from existing Strigo class

```shell-session
$ ztraining2strigo retrieve --help
usage: ztraining2strigo retrieve [-h] CLASS_ID

positional arguments:
  CLASS_ID    Existing Strigo class ID

optional arguments:
  -h, --help  show this help message and exit
```

This command can be used to create the [configuration](#configuration) from existing Strigo class.

- The configuration will be stored inside a `strigo.json` file at the root of your training (or one referenced by `--config`)
- The presentation filename will be searched recursively in the training directory and used in config if found, otherwise just prefixed with `PDF/`
- The presentation
- The init scripts will be downloaded into `Installation/strigo/init_<machine_name>.sh`
- The post launch scripts will be downloaded into `Installation/strigo/post_launch_<machine_name>.sh`

After launching this command, you can:
 - Edit the generated configuration
 - Reorganize the scripts to mutualize if possible/necessary

### Create configuration from scratch

```shell-session
$ ztraining2strigo create --help
usage: ztraining2strigo create [-h]

optional arguments:
  -h, --help  show this help message and exit
```

This command can be used to create a [configuration](#configuration) and the corresponding Strigo class.

- All necessary elements of a Strigo class will be asked interactively
- The configuration will be stored inside a `strigo.json` file at the root of your training (or one referenced by `--config`)
- The class will be created on Strigo

### Update Strigo class from configuration

```shell-session
$ ztraining2strigo update --help
usage: ztraining2strigo update [-h] [--dry-run] [--diff]

optional arguments:
  -h, --help     show this help message and exit
  --dry-run, -n  Do not perform update
  --diff, -d     Display diff of changes to apply in machines scripts
```

This command can be used to update a Strigo class from local [configuration](#configuration).

- Update is idempotent: if Strigo class is already as described by configuration, nothing will be done
- It is possible to check if an updated should be performed by using the `--dry-run` option

## Configuration

Configuration is stored in JSON format inside a `strigo.json` file at the root of your training (or one referenced by `--config`).

There is a [JSON Schema](https://json-schema.org/) available at <https://raw.githubusercontent.com/Zenika-Training/ztraining2strigo/main/strigo.schema.json>.

- `id`: the Strigo ID of the class, shouldn't be changed
- `name`: the name of the class
- `description`: the list of lines of description of the class (can be empty list `[]`)
- `presentations`: the list of presentation materials, can only contains 1 element for now (Strigo model)
  - `file`: the path to presentation file (typically `pdf/Zenika-Formation-xxx-Slides.pdf` or `pdf/Zenika-training-material-Slides.pdf`)
  - `notes_source`: the path to the listing of slides for notes extraction (should be `Slides/slides.json`)
- `resources`: the list of lab machines
  - `name`: the display name of the machine
  - `instance_type`: the size of the machine (one of `t2.medium`, `t2.large` or `t2.xlarge`, see [AWS EC2 T2 Instances](https://aws.amazon.com/ec2/instance-types/t2/#Product_Details))
  - `image`: the machine image, can be the normalized name of the preconfigured Strigo images (lower case, space replaced by simple hyphen `-`), or a custom image:
    - `image_id`: the AMI ID
    - `image_user`: the default user of the AMI
    - `ec2_region`: the region of the AMI
  - `init_scripts`: the list of init scripts to use for the machine, content of all the scripts will be concatenated into 1 init script in Strigo. Can be either:
    - a path to a local script
    - a reference to a script from [strigo-init-script-libs](https://github.com/Zenika/strigo-init-script-libs):
      - `script`: the filename of the script
      - `version`: the git version of the script to get (defaults to `main`)
      - `env`: the mapping of environment variables for the script
  - `post_launch_scripts`: the list of post launch batch scripts (Windows only) to use for the machine, content of all the scripts will be concatenated into 1 init script in Strigo. Same format as `init_scripts`
  - `webview_links`: the list of web interfaces of the machine:
    - `name`: the name of the interface
    - `url`: the URL of the interface (something of the form `http://instance.autolab.strigo.io:<port>`)

Example:

```json
{
  "$schema": "https://raw.githubusercontent.com/Zenika-Training/ztraining2strigo/main/strigo.schema.json",
  "name": "My training",
  "id": "43t8s3ZNSGwy89Ffo",
  "description": [
    "The description of the training",
    "",
    "Can be on multiple lines in a list"
  ],
  "presentations": [
    {
      "file": "pdf/Zenika-training-material-Slides.pdf",
      "notes_source": "Slides/slides.json"
    }
  ],
  "resources": [
    {
      "name": "machine1",
      "instance_type": "t2.medium",
      "image": "ubuntu-16.04.2",
      "init_scripts": [
        "Installation/strigo/init_all.sh",
        "Installation/strigo/init_machine1.sh",
        {
          "script": "code-server.sh",
          "env": {
            "code_server_version": "3.11.1",
            "code_server_extensions": "ms-azuretools.vscode-docker coenraads.bracket-pair-colorizer-2",
            "code_server_settings": "{\"workbench.colorTheme\": \"Default Dark+\"}"
          }
        }
      ],
      "post_launch_scripts": [],
      "webview_links": [
        {
          "name": "code-server",
          "url": "http://instance.autolab.strigo.io:9999"
        }
      ]
    },
    {
      "name": "machine2",
      "instance_type": "t2.xlarge",
      "image": {
        "image_id": "ami-0b209583a4a1146dd",
        "image_user": "ubuntu",
        "ec2_region": "eu-west-3"
      },
      "init_scripts": [
        "Installation/strigo/init_all.sh"
      ],
      "post_launch_scripts": [],
      "webview_links": []
    }
  ]
}
```

## Build package

Building requirement is a Python environment >= 3.7.

### Python wheel

```shell
./build.sh
```

### Windows binary

```powershell
.\build_windows.ps1
```

### Docker image

```shell
docker image build --tag zenika/ztraining2strigo .
```

## Debugging

You can activate HTTP traces by setting the environment variable `Z2S_TRACE_HTTP` to `1` or `True`.
