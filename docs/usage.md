# Usage

```python
from httpx import Client
from requestmodel import RequestModel, BaseModel
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
    url = "https://example.com/api/v1/my-endpoint/{param1}"

    param1: str  # will be used in the url
    param2: int  # will be converted as a query parameter

    # above is the same as
    param1: Annotated[str, Path()]  # will be used in the url
    param2: Annotated[int, Query()]  # will be converted as a query parameter


client = Client()

response = MyRequest(param1="foo", param2=42).send(client)

assert isinstance(response, MyResponse)
assert response.name
assert response.id
```
