# Ztraining2strigo

Create Strigo classe for Zenika training.

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

## Usage

1. Go to the root of your training
2. Launch any command of the `ztraining2strigo` binary

```shell-session
$ ztraining2strigo --help
usage: ztraining2strigo [-h] [--config CONFIG] COMMAND ...

positional arguments:
  COMMAND          sub-command help
    retrieve       Retrieve config from existing Strigo class

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

## Configuration

Configuration is stored in JSON format inside a `strigo.json` file at the root of your training (or one referenced by `--config`).

- `id`: the Strigo ID of the class, shouldn't be changed
- `name`: the name of the class
- `description`: the description of the class (can be `null` or empty)
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
  - `init_scripts`: the list of path to init scripts to use for the machine, content of all the scripts will be concatenated into 1 init script in Strigo
  - `post_launch_scripts`: the list of path to post launch batch scripts (Windows only) to use for the machine, content of all the scripts will be concatenated into 1 init script in Strigo
  - `webview_links`: the list of web interfaces of the machine:
    - `name`: the name of the interface
    - `url`: the URL of the interface (something of the form `http://instance.autolab.strigo.io:<port>`)

Example:

```json
{
  "id": "43t8s3ZNSGwy89Ffo",
  "name": "test infra4lab bis",
  "description": null,
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
        "Installation/strigo/init_machine1.sh"
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

## Python wheel

```shell
./build.sh
```

## Windows binary

```powershell
.\build_windows.ps1
```
