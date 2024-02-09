from typing import ClassVar
from typing import Literal
from typing import Optional
from typing import Type

from typing_extensions import Annotated

from requestmodel import RequestModel
from requestmodel.adapters.requests import RequestsRequestModel

from requestmodel.params import Query
from .models import LookupResponse


class LookupRequest(RequestModel[LookupResponse]):
    method: ClassVar[str] = "GET"
    url: ClassVar[str] = "lookup"
    response_model: ClassVar[Type[LookupResponse]] = LookupResponse

    id: str
    wt: Literal["json"] = "json"
    fl: Annotated[Optional[str], Query()] = None

    xyz: Optional[str] = None


class LookupRequests(RequestsRequestModel[LookupResponse]):
    method: ClassVar[str] = "GET"
    url: ClassVar[str] = "https://api.pdok.nl/bzk/locatieserver/search/v3_1/lookup"
    response_model: ClassVar[Type[LookupResponse]] = LookupResponse

    id: str
    wt: Literal["json"] = "json"
    fl: Annotated[Optional[str], Query()] = None

    xyz: Optional[str] = None
