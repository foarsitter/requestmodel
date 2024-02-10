import re
import types
from collections import deque
from dataclasses import is_dataclass
from typing import Any
from typing import Deque
from typing import Dict
from typing import FrozenSet
from typing import List
from typing import Mapping
from typing import Optional
from typing import Sequence
from typing import Set
from typing import Tuple
from typing import Union

from pydantic import BaseModel
from pydantic._internal._utils import lenient_issubclass
from pydantic.fields import FieldInfo
from typing_extensions import Annotated
from typing_extensions import get_args
from typing_extensions import get_origin

from . import params
from .typing import RequestArgs


UnionType = getattr(types, "UnionType", Union)

sequence_annotation_to_type = {
    Sequence: list,
    List: list,
    list: list,
    Tuple: tuple,
    tuple: tuple,
    Set: set,
    set: set,
    FrozenSet: frozenset,
    frozenset: frozenset,
    Deque: deque,
    deque: deque,
}

sequence_types = tuple(sequence_annotation_to_type.keys())


def _annotation_is_sequence(annotation: Any) -> bool:
    if lenient_issubclass(annotation, (str, bytes)):
        return False
    return lenient_issubclass(annotation, sequence_types)


def _annotation_is_complex(annotation: Any) -> bool:
    return (
        lenient_issubclass(annotation, (BaseModel, Mapping))
        or _annotation_is_sequence(annotation)
        or is_dataclass(annotation)
    )


def field_annotation_is_complex(
    annotation: Any,
) -> bool:
    origin = get_origin(annotation)
    if origin is Union or origin is UnionType:
        return any(field_annotation_is_complex(arg) for arg in get_args(annotation))

    return (
        _annotation_is_complex(annotation)
        or _annotation_is_complex(origin)
        or hasattr(origin, "__pydantic_core_schema__")
        or hasattr(origin, "__get_pydantic_core_schema__")
    )


def field_annotation_is_sequence(annotation: Any) -> bool:
    return _annotation_is_sequence(annotation) or _annotation_is_sequence(
        get_origin(annotation)
    )


def get_path_param_names(path: str) -> Set[str]:
    return set(re.findall("{(.*?)}", path))


def get_annotated_type(
    variable_key: str, variable_type: Any, path_param_names: Optional[Set[str]] = None
) -> FieldInfo:
    origin = get_origin(variable_type)

    annotated_property = None

    # check if we have a native type or an Annotated
    if origin is Annotated:
        origin, annotated_property = get_args(variable_type)

        is_complex = field_annotation_is_complex(origin)
        is_sequence = field_annotation_is_sequence(origin)
    else:
        origin = variable_type
        is_complex = field_annotation_is_complex(variable_type)
        is_sequence = field_annotation_is_sequence(variable_type)

    if annotated_property:
        annotated_property = annotated_property
    # when a key is present in the url, we annotate it as a path parameter
    elif path_param_names and variable_key in path_param_names:
        annotated_property = params.Path()
    elif is_complex and not is_sequence:
        annotated_property = params.Body()
    else:
        annotated_property = params.Query()

    scalar_types = (params.Query, params.Path, params.Header, params.Cookie)

    if isinstance(annotated_property, scalar_types) and is_complex:
        # query params do accept lists
        if not (isinstance(annotated_property, params.Query) and is_sequence):
            annotated_name = annotated_property.__class__.__name__

            # in 3.8 & 3.9 Dict does not have a __name__
            if not hasattr(origin, "__name__"):
                origin = get_origin(origin)
            raise ValueError(
                f"`{variable_key}` annotated as {annotated_name} "
                f"can only be a scalar, not a `{origin.__name__}`"
            )

    return annotated_property


def flatten_body(request_args: RequestArgs) -> None:
    body: Dict[str, Any] = {}
    for field_name, field_value in request_args[params.Body].items():
        body[field_name] = field_value
    request_args[params.Body] = body


def unify_body(
    annotated_property: Any, key: str, request_args: RequestArgs, value: Any
) -> None:
    if isinstance(value, dict):
        if annotated_property.embed:
            request_args[type(annotated_property)][key] = value
        else:
            for nested_key, nested_value in value.items():
                request_args[type(annotated_property)][nested_key] = nested_value
    else:
        request_args[type(annotated_property)][key] = value
