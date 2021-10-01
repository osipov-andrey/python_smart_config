from typing import List, Tuple, Union

import pytest
import yaml
from faker import Faker

from clever_config.actions import BaseAction, EnvLoaderAction
from clever_config.dict_traversal import dict_traversal
from clever_config.smart_config import TrickyConfig
from clever_config.utils import (
    IncompatiblePathAndMappingException,
    change_value_in_mapping,
)
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

    def test_pre_post_traversal_hooks(self):
        class TestActionOne(BaseAction):
            def __pre_traversal_hook__(self, mapping: dict) -> None:
                mapping["kekos"] = "lolero"

            def is_needed(self, path_chain: List[Union[str, int]], value: str) -> bool:
                return True

            def transform(self, path_chain: List[Union[str, int]], value: str) -> str:
                return value

        class TestActionTwo(TestActionOne):
            def __pre_traversal_hook__(self, mapping: dict) -> None:
                mapping["life"] = 42

            def __post_traversal_hook__(self, mapping: dict) -> None:
                mapping["life"] *= 2

        fake = Faker()
        Faker.seed(0)
        test_mapping = fake.pydict()
        dict_traversal(test_mapping, actions=[TestActionOne(), TestActionTwo()])
        assert test_mapping["kekos"] == "lolero"
        assert test_mapping["life"] == 84


class TestUtils:
    @staticmethod
    def _get_test_mapping():
        return {"a": [1, 2, {"b": "kek"}]}

    def test_change_value_in_mapping(self):
        mapping = self._get_test_mapping()
        change_value_in_mapping(mapping, "lol", ["a", 2, "b"])
        assert mapping["a"][2]["b"] == "lol"

    def test_empty_path(self):
        mapping = self._get_test_mapping()
        change_value_in_mapping(mapping, "lol", [])
        assert mapping["a"][2]["b"] == "kek"

    def test_wrong_path(self):
        mapping = self._get_test_mapping()
        with pytest.raises(IncompatiblePathAndMappingException):
            change_value_in_mapping(mapping, "lol", [1, 2, 3])
