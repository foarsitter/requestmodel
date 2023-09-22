from collections import defaultdict
from typing import Any
from typing import ClassVar
from typing import Dict
from typing import Generic
from typing import Optional
from typing import Type
from typing import TypeVar

import fastapi
import httpx
from fastapi import params
from fastapi.encoders import jsonable_encoder
from httpx import Request
from httpx._client import BaseClient
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic.fields import FieldInfo
from typing_extensions import get_type_hints


ResponseType = TypeVar("ResponseType", bound=BaseModel)

RequestArgs = Dict[Type[FieldInfo], Dict[str, Any]]


def get_annotated_type(v: Any) -> FieldInfo:
    if hasattr(v, "__metadata__"):
        annotated_property = v.__metadata__[0]
    else:
        annotated_property = fastapi.Query()
    return annotated_property


class RequestModel(BaseModel, Generic[ResponseType]):
    """Declarative way to define a model"""

    model_config = ConfigDict(populate_by_name=True)
    url: ClassVar[str]
    method: ClassVar[str]

    response_model: ClassVar[Type[ResponseType]]  # type: ignore[misc]

    body: Optional[ResponseType] = None

    def as_request(self, client: BaseClient) -> Request:
        """Transform the properties of the object into a request"""

        request_args: RequestArgs = defaultdict(dict)

        # we exclude unset properties from the request
        values = self.model_dump(exclude_unset=True)

        self.request_args_for_values(request_args, values)

        _params = (
            jsonable_encoder(request_args[params.Query], exclude_unset=True)
            if request_args[params.Query]
            else None
        )
        headers = (
            jsonable_encoder(request_args[params.Header])
            if request_args[params.Header]
            else {}
        )
        cookies = (
            jsonable_encoder(request_args[params.Cookie])
            if request_args[params.Cookie]
            else None
        )
        files = (
            jsonable_encoder(request_args[params.File])
            if request_args[params.File]
            else None
        )
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

    def request_args_for_values(
        self, request_args: RequestArgs, values: Dict[str, Any]
    ) -> None:

        skip_properties = ["url", "method", "response_model", "body"]

        for k, v in get_type_hints(self.__class__, include_extras=True).items():

            if k in skip_properties:
                continue

            annotated_property = get_annotated_type(v)

            value = values.get(k, None)

            if not value and getattr(self, k, None) is not None:
                value = getattr(self, k)

            if value:
                request_args[type(annotated_property)][k] = value

    def send(self, client: httpx.Client) -> ResponseType:
        """Send the request synchronously"""
        r = self.as_request(client)
        response = client.send(r)
        response.raise_for_status()
        return self.response_model.model_validate(response.json())

    async def asend(self, client: httpx.AsyncClient) -> ResponseType:
        """Send the request asynchronously"""
        r = self.as_request(client)
        response = await client.send(r)
        return self.response_model.model_validate(response.json())
