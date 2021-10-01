from typing import Any, List, Union

KeyOrIndex = Union[str, int]


class IncompatiblePathAndMappingException(Exception):
    pass


def change_value_in_mapping(mapping: dict, value: Any, path: List[KeyOrIndex]) -> None:
    value_step: Union[dict, list] = mapping
    for path_step in path:
        try:
            next_step = value_step[path_step]  # type: ignore
        except (KeyError, IndexError):
            raise IncompatiblePathAndMappingException(f"Wrong path: {path}")
        if isinstance(next_step, dict) or isinstance(next_step, list):
            value_step = next_step
        else:
            value_step[path_step] = value  # type: ignore
            break
