from typing import ClassVar
from typing import Literal
from typing import Optional
from typing import Type

from fastapi import Query
from httpx import HTTPStatusError
from httpx import Response
from typing_extensions import Annotated

from requestmodel import RequestModel

from .models import LookupResponse


class LookupRequest(RequestModel[LookupResponse]):
    method: ClassVar[str] = "GET"
    url: ClassVar[str] = "lookup"
    response_model: ClassVar[Type[LookupResponse]] = LookupResponse

    id: str
    wt: Literal["json"] = "json"
    fl: Annotated[Optional[str], Query()] = None

    xyz: Optional[str] = None

    def handle_error(self, response: Response) -> None:
        try:
            super().handle_error(response)
        except HTTPStatusError as e:
            raise Exception(e.response.content) from e
