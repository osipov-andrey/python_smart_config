import abc
from os import getenv
from typing import List, Optional, Union


class ActionException(Exception):
    pass


class BaseAction(abc.ABC):
    def conditionally_transform(self, path_chain: List[Union[str, int]], value: str) -> str:
        if self.is_needed(path_chain, value):
            return self.transform(path_chain, value)
        return value

    @staticmethod
    def path_to_str(path_chain: List[Union[str, int]]) -> str:
        return " -> ".join(str(el) for el in path_chain)

    @abc.abstractmethod
    def is_needed(self, path_chain: List[Union[str, int]], value: str) -> bool:
        pass

    @abc.abstractmethod
    def transform(self, path_chain: List[Union[str, int]], value: str) -> str:
        pass

    def __pre_traversal_hook__(self, mapping: dict) -> None:
        pass

    def __post_traversal_hook__(self, mapping: dict) -> None:
        pass


class EnvLoaderAction(BaseAction):
    ENV_PLACEHOLDER_PREFIX = "ENV__"

    def is_needed(self, path_chain: List[Union[str, int]], value: str) -> bool:
        return value.startswith(self.ENV_PLACEHOLDER_PREFIX)

    def transform(self, path_chain: List[Union[str, int]], value: str) -> str:
        expected_var_name: str = value.replace(self.ENV_PLACEHOLDER_PREFIX, "")
        value_: Optional[str] = getenv(expected_var_name)
        if not value_:
            raise ActionException(f"Broken ENV Variable: {expected_var_name}! Path: {self.path_to_str(path_chain)}")
        return value_
