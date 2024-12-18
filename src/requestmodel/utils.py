from typing import Any
from typing import Dict
from typing import Optional
from typing import Set

from pydantic.fields import FieldInfo
from typing_extensions import Annotated
from typing_extensions import get_args
from typing_extensions import get_origin

from . import params
from .fastapi import field_annotation_is_complex
from .fastapi import field_annotation_is_sequence
from .typing import RequestArgs


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
