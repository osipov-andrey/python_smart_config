import abc
from os import getenv
from typing import Optional


class ActionException(Exception):
    pass


class Action(abc.ABC):

    # def conditionally_transform(self, path_chain: List[Union[str,int]], value: str) -> str:  # TODO
    def conditionally_transform(self, value: str) -> str:
        if self.is_needed(value):
            return self.transform(value)
        return value

    @abc.abstractmethod
    def is_needed(self, value: str) -> bool:
        pass

    @abc.abstractmethod
    def transform(self, value: str) -> str:
        pass


class EnvLoader(Action):
    ENV_PLACEHOLDER_PREFIX = "ENV__"

    def is_needed(self, value: str) -> bool:
        return value.startswith(self.ENV_PLACEHOLDER_PREFIX)

    def transform(self, value: str) -> str:
        expected_var_name: str = value.replace(self.ENV_PLACEHOLDER_PREFIX, "")
        value_: Optional[str] = getenv(expected_var_name)
        if not value_:
            raise ActionException(
                # f"Broken ENV Variable: {expected_var_name}!\n\tPath: {' -> '.join(path_chain)}"  # TODO
                f"Broken ENV Variable: {expected_var_name}!"
            )
        return value_
