from typing import Any
from typing import ClassVar
from typing import Dict
from typing import Generic
from typing import Iterator
from typing import Optional
from typing import Set
from typing import Type
from typing import TypeVar

from fastapi._compat import field_annotation_is_complex
from fastapi._compat import field_annotation_is_sequence
from fastapi.utils import get_path_param_names
from httpx import AsyncClient
from httpx import Client
from httpx import Request
from httpx import Response
from httpx._client import BaseClient
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic.fields import FieldInfo
from typing_extensions import Annotated
from typing_extensions import get_args
from typing_extensions import get_origin
from typing_extensions import get_type_hints
from typing_extensions import override

from requestmodel import params

from .encoders import jsonable_encoder


ResponseType = TypeVar("ResponseType", bound=BaseModel)

RequestArgs = Dict[Type[FieldInfo], Dict[str, Any]]


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


class RequestModel(BaseModel, Generic[ResponseType]):
    """Declarative way to define a model"""

    model_config = ConfigDict(populate_by_name=True)
    url: ClassVar[str]
    method: ClassVar[str]

    response_model: ClassVar[Type[ResponseType]]  # type: ignore[misc]

    def get_path_param_names(self) -> Set[str]:
        return get_path_param_names(self.url)

    def as_request(self, client: BaseClient) -> Request:
        """Transform the properties of the object into a request"""

        request_args = self.request_args_for_values()

        headers = request_args[params.Header]
        body = request_args[params.Body]

        is_json_request = "json" in headers.get("content-type", "")

        r = Request(
            method=self.method,
            url=client._merge_url(self.url.format(**request_args[params.Path])),
            params=request_args[params.Query],
            headers=headers,
            cookies=request_args[params.Cookie],
            files=request_args[params.File],
            data=body if not is_json_request else None,
            json=body if is_json_request else None,
        )

        return r

    def request_args_for_values(self) -> RequestArgs:
        request_args: RequestArgs = {
            params.Query: {},
            params.Path: {},
            params.Cookie: {},
            params.Header: {},
            params.File: {},
            params.Body: {},
        }

        # we exclude unset properties from the request
        values = jsonable_encoder(self, exclude_unset=True)
        path_param_names = self.get_path_param_names()

        for key, field in get_type_hints(self.__class__, include_extras=True).items():
            if getattr(field, "__origin__", None) is ClassVar:
                continue

            annotated_property = get_annotated_type(key, field, path_param_names)

            if key in values:
                value = values[key]
            else:
                if getattr(self, key, None) is not None:
                    value = jsonable_encoder(getattr(self, key))
                else:
                    continue

            if (
                isinstance(annotated_property, params.Header)
                and annotated_property.convert_underscores
            ):
                key = key.replace("_", "-")

            if isinstance(annotated_property, params.Body):
                unify_body(annotated_property, key, request_args, value)
            else:
                request_args[type(annotated_property)][key] = value

        flatten_body(request_args)

        return request_args

    def send(self, client: Client) -> ResponseType:
        """Send the request synchronously"""
        r = self.as_request(client)
        response = client.send(r)
        self.handle_error(response)
        return self.response_model.model_validate(response.json())

    def handle_error(self, response: Response) -> None:
        response.raise_for_status()

    async def asend(self, client: AsyncClient) -> ResponseType:
        """Send the request asynchronously"""
        r = self.as_request(client)
        response = await client.send(r)
        self.handle_error(response)
        return self.response_model.model_validate(response.json())


class IteratorRequestModel(RequestModel[ResponseType]):
    def next(self, response: ResponseType) -> bool:  # pragma: no cover
        raise NotImplementedError

    @override
    def send(self, client: Client) -> Iterator[ResponseType]:  # type: ignore[override]
        response = super().send(client)
        yield response

        while self.next(response):
            response = super().send(client)
            yield response
