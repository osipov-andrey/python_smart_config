from typing import Any, List, Tuple, Union

from clever_config.actions import ActionException, BaseAction

JSONTypes = Union[dict, list, str, int]
PathList = List[Union[str, int]]
CheckedCollection = Union[dict, list]


def dict_traversal(mapping: dict, actions: List[BaseAction]) -> List[str]:

    queue: List[Tuple[PathList, CheckedCollection]] = [
        ([], mapping),
    ]
    errors = []

    def _check_value(path_: PathList, checking_value: JSONTypes) -> None:
        nonlocal queue
        nonlocal errors

        # CHECK DICT:
        if _is_dict(checking_value):
            queue.append((path_, checking_value))  # type: ignore
            # Type already checked
            return

        # CHECK LIST:
        elif _is_list(checking_value):
            for index, _item in enumerate(checking_value):  # type: ignore
                extended_path = _get_extended_path(path_, index)
                # Type already checked
                # CHECK STR IN LIST:
                if not _is_str_or_digit(_item):
                    queue.append((extended_path, _item))
                    continue
                _errors = _run_all_actions(extended_path, checking_value, actions)  # type: ignore
                # Type already checked
                errors.extend(_errors)
            return

        # CHECK STR OR INT
        if _is_str_or_digit(checking_value):
            _errors = _run_all_actions(path_, dict_or_list, actions)  # type: ignore
            # Type already checked
            errors.extend(_errors)

    for path, dict_or_list in queue:  # type: PathList, CheckedCollection
        if _is_dict(dict_or_list):
            for key_or_index, value in dict_or_list.items():  # type: ignore
                # Type already checked
                _check_value(_get_extended_path(path, key_or_index), value)
        elif _is_list(dict_or_list):
            for key_or_index, item in enumerate(dict_or_list):
                _check_value(_get_extended_path(path, key_or_index), item)

    return errors


def _run_all_actions(
    path: PathList,
    dict_or_list: Union[dict, list],
    actions: List[BaseAction],
) -> list:

    key_or_index: Union[str, int] = path[-1]
    errors: list = []

    for action in actions:  # type: BaseAction
        value: Union[int, str] = dict_or_list[key_or_index]  # type: ignore
        if isinstance(value, int):
            return errors
        try:
            dict_or_list[key_or_index] = action.conditionally_transform(path, value)  # type: ignore
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


def _get_extended_path(path_list: PathList, new_value: Union[str, int]) -> PathList:
    new_path_list = list(path_list)
    new_path_list.append(new_value)
    return new_path_list
