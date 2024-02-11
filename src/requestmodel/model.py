from typing import ClassVar
from typing import Generic
from typing import Iterator
from typing import Optional
from typing import Set
from typing import Type

from httpx import AsyncClient
from httpx import Client
from httpx import Request
from httpx import Response
from httpx._client import BaseClient
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import TypeAdapter
from typing_extensions import get_type_hints
from typing_extensions import override

from . import params
from .fastapi import get_path_param_names
from .fastapi import jsonable_encoder
from .typing import RequestArgs
from .typing import ResponseType
from .utils import flatten_body
from .utils import get_annotated_type
from .utils import unify_body


class BaseRequestModel(BaseModel, Generic[ResponseType]):
    """Declarative way to define a model"""

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)
    url: ClassVar[str]
    method: ClassVar[str]

    response_model: ClassVar[Type[ResponseType]]  # type: ignore[misc]

    def get_path_param_names(self) -> Set[str]:
        return get_path_param_names(self.url)

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

            if annotated_property.exclude:
                continue

            if key in values:
                value = values[key]
            else:
                if getattr(self, key, None) is not None:
                    value = jsonable_encoder(getattr(self, key))
                else:
                    continue

            attr_name = annotated_property.alias or key

            if (
                isinstance(annotated_property, params.Header)
                and annotated_property.convert_underscores
            ):
                attr_name = attr_name.replace("_", "-")

            if isinstance(annotated_property, params.Body):
                unify_body(annotated_property, attr_name, request_args, value)
            else:
                request_args[type(annotated_property)][attr_name] = value

        flatten_body(request_args)

        return request_args


class RequestModel(BaseRequestModel[ResponseType]):
    raw_response: Optional[Response] = None

    def handle_error(self, response: Response) -> None:
        response.raise_for_status()

    def send(self, client: Client) -> ResponseType:
        """Send the request synchronously"""
        r = self.as_request(client)
        self.raw_response = client.send(r)
        self.handle_error(self.raw_response)
        if isinstance(self.response_model, TypeAdapter):
            return self.response_model.validate_python(self.raw_response.json())
        return self.response_model.model_validate(self.raw_response.json())

    async def asend(self, client: AsyncClient) -> ResponseType:
        """Send the request asynchronously"""
        r = self.as_request(client)
        self.raw_response = await client.send(r)
        self.handle_error(self.raw_response)
        return self.response_model.model_validate(self.raw_response.json())

    def as_request(self, client: BaseClient) -> Request:
        """Transform the properties of the object into a request"""

        from .adapters.httpx import HTTPXAdapter

        adapter = HTTPXAdapter()
        return adapter.transform(client, self)


class IteratorRequestModel(RequestModel[ResponseType]):
    raw_response: Optional[Response] = None

    def next_from_response(self, response: ResponseType) -> bool:  # pragma: no cover
        """
        Prepare the current object for the next request and return true

        In case of cursor pagination set the next token
        In case of offset pagination increment the offset

        """
        raise NotImplementedError

    @override
    def send(self, client: Client) -> Iterator[ResponseType]:  # type: ignore[override]
        response = super().send(client)
        yield response

        while self.next_from_response(response):
            # avoid serializing the response
            self.raw_response = None
            response = super().send(client)
            yield response
