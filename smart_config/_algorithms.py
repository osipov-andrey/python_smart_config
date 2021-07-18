from typing import Mapping, List, Callable, Union, Optional, Any

from smart_config_old._actions import ActionException

JSONTypes = Union[dict, list, str, int]


class ConfigPath:

    def __init__(self, root: str):
        self._path = [root, ]

    def join(self, path_step: Union[int, str]) -> 'ConfigPath':
        self._path.append(path_step)
        return self

    def resolve(self, config: dict) -> JSONTypes:
        value: JSONTypes = config
        for path_step in self._path:
            value = value[path_step]
        return value


def run_all_actions(
        value: str,
        dict_or_list: Union[dict, list],
        key_or_index: Union[str, int],
        actions: List[Callable]
) -> list:
    errors: list = []
    for action in actions:  # type: Callable
        try:
            dict_or_list[key_or_index] = action(value)
        except ActionException as err:
            errors.append(str(err))
    return errors


def _is_dict(obj: Any) -> bool:
    return isinstance(obj, dict)


def _is_list(obj: Any) -> bool:
    return isinstance(obj, list)


def _is_str_or_digit(obj: Any) -> bool:
    return bool(any((isinstance(obj, str), isinstance(obj, int))))


def dict_traversal(mapping: Mapping, actions: List[Callable]) -> List[str]:
    queue: List[Union[Mapping, List]] = [mapping, ]
    errors = []

    def _check_value(checking_value: JSONTypes) -> None:
        nonlocal queue
        nonlocal errors

        # CHECK DICT
        if _is_dict(checking_value):
            queue.append(checking_value)
            return

        # CHECK LIST
        elif _is_list(checking_value):
            for index, _item in enumerate(checking_value):
                # CHECK STR IN LIST
                # if not _is_str_or_digit(checking_value):
                if not any((isinstance(_item, str), isinstance(_item, int))):
                    queue.append(_item)
                    continue
                _errors: list = run_all_actions(_item, checking_value, index, actions)
                errors.extend(_errors)
            return

        # CHECK STR OR INT
        nonlocal dict_or_list
        nonlocal key_or_index
        _errors: list = run_all_actions(checking_value, dict_or_list, key_or_index, actions)
        errors.extend(_errors)

    for dict_or_list in queue:  # type: Union[dict, list]
        if _is_dict(dict_or_list):
            for key_or_index, value in dict_or_list.items():
                _check_value(value)
        elif _is_list(dict_or_list):
            for key_or_index, item in enumerate(dict_or_list):
                _check_value(item)

    return errors
