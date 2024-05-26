# Usage

```python
from httpx import Client
from pydantic import BaseModel

from requestmodel import RequestModel
from requestmodel.params import Path, Query
from typing_extensions import Annotated


# define your response,
# preferably we generate it with datamodel-code-generator based on an OpenAPI spec
class MyResponse(BaseModel):
    id: int
    name: str


# describe your request
# the goal is to follow the rules FastAPI uses to describe endpoints
class MyRequest(RequestModel[MyResponse]):
    method = "GET"
    url = "/api/v1/my-endpoint/{param1}"

    param1: str  # will be used in the url
    param2: int  # will be converted as a query parameter

    # above is the same as
    param1: Annotated[str, Path()]  # will be used in the url
    param2: Annotated[int, Query()]  # will be converted as a query parameter

    # the generic type should match with response_model so we can use it to deserialize the request
    response_model = MyResponse


client = Client(base_url="https://example.com")

response = MyRequest(param1="foo", param2=42).send(client)

assert isinstance(response, MyResponse)
assert response.name
assert response.id
```

There is also an IterableRequestModel
that can be used for paginated responses by implementing `IteratorRequestModel.next()`

```python
from typing import List, Optional

from httpx import Client
from pydantic import BaseModel

from requestmodel import IteratorRequestModel


class MyResponse(BaseModel):
    id: int
    name: str


class PaginatedMyResponse(BaseModel):
    results: List[MyResponse]
    next: Optional[str]


class MyPaginatedRequest(IteratorRequestModel[PaginatedMyResponse]):
    method = "GET"
    url = "https://example.com/api/v1/my-endpoint/{param1}"

    param1: str  # will be used in the url
    param2: int  # will be converted as a query parameter

    next: Optional[str] = None  # will be used to paginate

    # the generic type should match with response_model so we can use it to deserialize the request
    response_model = PaginatedMyResponse

    def next_from_response(self, response: PaginatedMyResponse) -> bool:
        # update the new request arguments
        self.next = response.next
        return self.next is not None


client = Client()

request = MyPaginatedRequest(param1="foo", param2=42)

for response in request.send(client):
    assert isinstance(response, MyResponse)
    assert response.name
    assert response.id

```
