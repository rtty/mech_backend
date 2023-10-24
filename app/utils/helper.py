import uuid
from typing import Any, Dict, List, Optional

from app.exceptions.http import HttpException


def get_default_string(value: str, default: str) -> str:
    """
    Get default value

    :param value: value
    :param default: default value
    :return: value
    """
    if value is None or value == '':
        return default
    else:
        return value


def check_required(field: str, value: Any) -> None:
    """
    Check if not None

    :param field: field name for exception
    :param value: value
    :return: void
    """
    if value is None:
        raise HttpException(400, field + ' is required')


def check_int(field: str, value: int) -> None:
    """
    Check integer

    :param field: field name for exception
    :param value: value
    :return: void
    """
    try:
        value = int(value)
    except ValueError:
        raise HttpException(400, field + ' must be an integer')

    if value < 0:
        raise HttpException(400, field + ' must be an positive integer')


def check_string(field: str, value: str) -> None:
    """
    Check string

    :param field: field name for exception
    :param value: value
    :return: void
    """
    if type(value) is not str:
        raise HttpException(400, field + ' must be a string')


def check_array(field: str, value: Optional[List[Any]]) -> None:
    """
    Check array

    :param field: field name for exception
    :param value: value
    :return: void
    """
    if not isinstance(value, list):
        raise HttpException(400, field + ' must be an array')


def check_array_item(field: str, value: List[Any], item_type: str) -> None:
    """
    Check array item type

    :param field: field name for exception
    :param value: array
    :param item_type: item type
    :return: void
    """
    # check is array
    check_array(field, value)

    # check array item type
    for item in value:
        if item_type == 'int':
            check_int(field, item)
        elif item_type == 'string':
            check_string(field, item)


def check_choices(field: str, value: str, choices: List[str]) -> None:
    """
    Check value is in choices

    :param field: field name for exception
    :param value: value
    :param choices: available value list
    :return: void
    """
    if value not in choices:
        raise HttpException(400, field + ' should be one of these: ' + ', '.join(choices))


def check_token(field: str, value: Optional[str]) -> None:
    check_required(field, value)
    check_string(field, value)
    try:
        token = uuid.UUID(value, version=4)
        if token.hex != value.replace('-', ''):
            raise ValueError()
    except ValueError:
        raise HttpException(400, field + ' is not a valid token')
