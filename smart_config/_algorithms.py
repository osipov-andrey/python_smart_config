from typing import Any, Callable, List, Union

from smart_config._actions import ActionException

JSONTypes = Union[dict, list, str, int]


class ConfigPath:
    def __init__(self, root: str):
        self._path: List[Union[int, str]] = [
            root,
        ]

    def join(self, path_step: Union[int, str]) -> "ConfigPath":
        self._path.append(path_step)
        return self

    def resolve(self, config: dict) -> JSONTypes:
        value: Union[dict, list] = config
        for path_step in self._path:
            value = value[path_step]  # type: ignore
            # Here we combine dicts and lists
        return value


def run_all_actions(
    value: Union[int, str],
    dict_or_list: Union[dict, list],
    key_or_index: Union[str, int],
    actions: List[Callable],
) -> list:
    errors: list = []
    for action in actions:  # type: Callable
        try:
            dict_or_list[key_or_index] = action(value)  # type: ignore
            # Here we combine dicts and lists
        except ActionException as err:
            errors.append(str(err))
    return errors


def _is_dict(obj: Any) -> bool:
    return isinstance(obj, dict)


def _is_list(obj: Any) -> bool:
    return isinstance(obj, list)


def _is_str_or_digit(obj: Any) -> bool:
    return any((isinstance(obj, str), isinstance(obj, int)))


def dict_traversal(mapping: dict, actions: List[Callable]) -> List[str]:
    queue: List[Union[dict, list]] = [
        mapping,
    ]
    errors = []

    def _check_value(checking_value: JSONTypes) -> None:
        nonlocal queue
        nonlocal errors

        # CHECK DICT:
        if _is_dict(checking_value):
            queue.append(checking_value)  # type: ignore
            # Type already checked
            return

        # CHECK LIST:
        elif _is_list(checking_value):
            for index, _item in enumerate(checking_value):  # type: ignore
                # Type already checked
                # CHECK STR IN LIST:
                # if not _is_str_or_digit(checking_value):
                if not _is_str_or_digit(_item):
                    queue.append(_item)
                    continue
                _errors = run_all_actions(_item, checking_value, index, actions)  # type: ignore
                # Type already checked
                errors.extend(_errors)
            return

        # CHECK STR OR INT
        if _is_str_or_digit(checking_value):
            _errors = run_all_actions(
                checking_value, dict_or_list, key_or_index, actions  # type: ignore
            )
            # Type already checked
            errors.extend(_errors)

    for dict_or_list in queue:  # type: Union[dict, list]
        if _is_dict(dict_or_list):
            for key_or_index, value in dict_or_list.items():  # type: ignore
                # Type already checked
                _check_value(value)
        elif _is_list(dict_or_list):
            for key_or_index, item in enumerate(dict_or_list):
                _check_value(item)

    return errors
