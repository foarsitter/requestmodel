from typing import Any
from typing import ClassVar
from typing import Dict
from typing import Generic
from typing import Iterator
from typing import Optional
from typing import Type
from typing import TypeVar

from httpx import AsyncClient
from httpx import Client
from httpx import Request
from httpx._client import BaseClient
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic.fields import FieldInfo
from typing_extensions import get_type_hints
from typing_extensions import override

from requestmodel import params

from .encoders import jsonable_encoder


ResponseType = TypeVar("ResponseType", bound=BaseModel)

RequestArgs = Dict[Type[FieldInfo], Dict[str, Any]]


class RequestModel(BaseModel, Generic[ResponseType]):
    """Declarative way to define a model"""

    model_config = ConfigDict(populate_by_name=True)
    url: ClassVar[str]
    method: ClassVar[str]

    response_model: ClassVar[Type[ResponseType]]  # type: ignore[misc]

    body: Optional[ResponseType] = None

    def get_annotated_type(self, variable_key: str, variable_type: Any) -> FieldInfo:
        if hasattr(variable_type, "__metadata__"):
            annotated_property = variable_type.__metadata__[0]
        # when a key is present in the url we annotate it as a path parameter
        elif f"{{{variable_key}}}" in self.url:
            annotated_property = params.Path()
        else:
            annotated_property = params.Query()
        return annotated_property

    def as_request(self, client: BaseClient) -> Request:
        """Transform the properties of the object into a request"""

        request_args: RequestArgs = {
            params.Query: {},
            params.Path: {},
            params.Cookie: {},
            params.Header: {},
            params.File: {},
        }

        self.request_args_for_values(request_args)

        _params = request_args[params.Query]
        headers = request_args[params.Header]
        cookies = request_args[params.Cookie]
        files = request_args[params.File]

        body = jsonable_encoder(self.body) if self.body else None

        headers["accept"] = "application/json"

        r = Request(
            method=self.method,
            url=client._merge_url(self.url.format(**request_args[params.Path])),
            params=_params,
            headers=headers,
            cookies=cookies,
            files=files,
            json=body,
        )

        return r

    def request_args_for_values(self, request_args: RequestArgs) -> None:
        # we exclude unset properties from the request
        values = jsonable_encoder(self, exclude_unset=True)

        skip_properties = ["url", "method", "response_model", "body"]

        for k, v in get_type_hints(self.__class__, include_extras=True).items():
            if k in skip_properties:
                continue

            annotated_property = self.get_annotated_type(k, v)

            value = values.get(k, None)

            if not value and getattr(self, k, None) is not None:
                value = jsonable_encoder(getattr(self, k))

            if (
                isinstance(annotated_property, params.Header)
                and annotated_property.convert_underscores
            ):
                k = k.replace("_", "-")

            if value:
                request_args[type(annotated_property)][k] = value

    def send(self, client: Client) -> ResponseType:
        """Send the request synchronously"""
        r = self.as_request(client)
        response = client.send(r)
        response.raise_for_status()
        return self.response_model.model_validate(response.json())

    async def asend(self, client: AsyncClient) -> ResponseType:
        """Send the request asynchronously"""
        r = self.as_request(client)
        response = await client.send(r)
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
