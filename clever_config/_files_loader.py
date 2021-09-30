import json
from enum import Enum
from os import listdir
from os.path import isfile
from pathlib import Path
from typing import List

import yaml
from attributedict.collections import AttributeDict
from pydantic import BaseModel


class FileFormats(str, Enum):
    JSON = "json"
    YAMl = "yaml"
    YML = "yml"


class ConfigFile(BaseModel):
    path: Path
    environment: str
    format: FileFormats


def get_config_files(
    path: str,
) -> List[ConfigFile]:
    """

    :param path: relative path to directory with files
    :return:
    """
    config_files: List[ConfigFile] = []
    abs_path: Path = Path(path)
    files: List[Path] = [abs_path.joinpath(f) for f in listdir(str(abs_path)) if isfile(str(abs_path.joinpath(f)))]
    for f in files:  # type: Path
        file_name, format_ = f.absolute().name.split(".")
        _, env = file_name.split("_")
        config_files.append(
            ConfigFile(
                path=f,
                environment=env,
                format=format_,
            )
        )
    return config_files


def load_config(config_file: ConfigFile) -> AttributeDict:
    with open(config_file.path.absolute(), "r") as f:
        if config_file.format == FileFormats.JSON:
            config: dict = json.load(f)
        else:
            config = yaml.safe_load(f)
    return AttributeDict(config)
