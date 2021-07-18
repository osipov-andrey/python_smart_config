from os import getenv
from typing import Tuple

DEFAULT_ENV_PLACEHOLDER_PREFIX = "ENV__"


class ActionException(Exception):
    pass


def _load_env_value(env_var_name_with_prefix: str) -> Tuple[str, str]:
    expected_var_name = env_var_name_with_prefix.replace(DEFAULT_ENV_PLACEHOLDER_PREFIX, "")
    value_ = getenv(expected_var_name)
    return value_, expected_var_name


def check_env_loader_action(value: str) -> str:
    if not isinstance(value, str) or not value.startswith(DEFAULT_ENV_PLACEHOLDER_PREFIX):
        return value
    value, expected_var_name = _load_env_value(value)
    if not value:
        raise ActionException(f"Broken ENV Variable: {expected_var_name}!")
    return value
