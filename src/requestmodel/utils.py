from typing import Union, Type, Any, Set

from fastapi import _compat, utils


def field_annotation_is_complex(annotation: Union[Type[Any], None]) -> bool:
    return _compat.field_annotation_is_complex(annotation)


def field_annotation_is_sequence(annotation: Union[Type[Any], None]) -> bool:
    return _compat.field_annotation_is_sequence(annotation)


def get_path_param_names(path: str) -> Set[str]:
    return utils.get_path_param_names(path)
