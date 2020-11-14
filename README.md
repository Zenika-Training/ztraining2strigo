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

```shell
ztraining2strigo --help
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
