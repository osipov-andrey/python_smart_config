import os
from pathlib import Path
from typing import Generator, List, Tuple

import pytest
import yaml

from smart_config._algorithms import ConfigPath
from smart_config.smart_config import ConfigWithEnvironment, TrickyConfig

path_to_config: Path = Path(__file__).parent.absolute().joinpath("configs")


def test_1():
    config = TrickyConfig(str(path_to_config))
    assert config.prod


def test_attribute_error():
    config: TrickyConfig = TrickyConfig(str(path_to_config))
    with pytest.raises(AttributeError) as err:
        assert config.foobar
        assert err.value.args == "foobar"


def test_config_with_env():
    config = ConfigWithEnvironment(str(path_to_config))
    assert config.prod
    assert config.dev


@pytest.fixture
def config_file() -> Generator[Tuple[str, List[str]], None, None]:
    file_name = path_to_config.joinpath("config_test.yml")

    config_ = {
        "f1": "ENV__VARIABLE_0",
        "f2": {
            "s1": ["foo", "bar"],
        },
        "f3": {"s1": {"t1": "ENV__VARIABLE"}},
        "f4": {
            "s1": ["a", "", 42],
            "s2": ["d", "f", "ENV__VARIABLE_2"],
        },
        "f5": [
            ["kek", "ENV__VARIABLE_3"],
            {"t1": ["lol", "ENV__VARIABLE_4"]},
        ],
    }
    expected_vars = [
        "VARIABLE_0",
        "VARIABLE",
        "VARIABLE_2",
        "VARIABLE_3",
        "VARIABLE_4",
    ]

    with open(file_name, "w") as f:
        yaml.dump(config_, f)

    yield str(file_name), expected_vars

    os.remove(file_name)


@pytest.fixture
def config_file_with_env(config_file: Tuple[str, List[str]]) -> Generator[Tuple[str, str], None, None]:
    file_name, expected_vars = config_file  # type: str, List[str]

    test_value: str = "TEST"

    for var in expected_vars:
        os.environ[var] = test_value

    yield file_name, test_value

    for var in expected_vars:
        os.environ.pop(var)
        assert os.getenv(var) is None


class TestConfig:
    def test_check_env(self, config_file: Tuple[str, List[str]]):
        file_name, expected_errors = config_file

        with pytest.raises(RuntimeError) as exc_info:
            ConfigWithEnvironment(str(path_to_config))
            for error in expected_errors:
                assert error in str(exc_info)

    def test_fill_from_env(self, config_file_with_env: Tuple[str, str]):
        file_name, expected_value = config_file_with_env  # type: str, str

        config = ConfigWithEnvironment(str(path_to_config))

        assert config.test["f1"] == expected_value
        assert config.test["f3"]["s1"]["t1"] == expected_value
        assert config.test["f4"]["s2"][2] == expected_value
        assert config.test["f5"][0][1] == expected_value
        assert config.test["f5"][1]["t1"][1] == expected_value


def test_config_path():
    config = {
        "a": 1,
        "b": 2,
        "c": {
            "a1": 1,
            "b1": [1, 2, 3, {"a11": "kek"}],
        },
    }
    assert ConfigPath("c").join("b1").join(3).join("a11").resolve(config) == "kek"
