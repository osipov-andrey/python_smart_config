from typing import List, Tuple

import pytest
import yaml

from clever_config.actions import EnvLoaderAction
from clever_config.dict_traversal import dict_traversal
from clever_config.smart_config import TrickyConfig
from tests.conftest import path_to_config


class TestTrickyConfig:
    def test_1(self):
        config = TrickyConfig(str(path_to_config))
        assert config.prod

    def test_attribute_error(self):
        config: TrickyConfig = TrickyConfig(str(path_to_config))
        with pytest.raises(AttributeError) as err:
            assert config.foobar
            assert err.value.args == "foobar"

    def test_config_with_env(self):
        config = TrickyConfig(str(path_to_config), actions=[EnvLoaderAction()])
        assert config.prod
        assert config.dev

    def test_fill_tricky_config_from_env(self, config_file_with_env: Tuple[str, str]):
        file_name, expected_value = config_file_with_env  # type: str, str

        config = TrickyConfig(str(path_to_config), actions=[EnvLoaderAction()])

        assert config.test["f1"] == expected_value
        assert config.test["f3"]["s1"]["t1"] == expected_value
        assert config.test["f4"]["s2"][2] == expected_value
        assert config.test["f5"][0][1] == expected_value
        assert config.test["f5"][1]["t1"][1] == expected_value


class TestDictTraversal:
    def test_check_env(self, config_file: Tuple[str, List[str]]):
        file_name, expected_errors = config_file
        with open(file_name, "r") as f:
            config: dict = yaml.safe_load(f)

        errors = dict_traversal(config, [EnvLoaderAction()])

        for error in expected_errors:
            assert error in str(errors)
