from requestmodel.typing import ResponseType

# Recipes

This document outlines some special cases you will encounter in the wild.

## Headers with dashes

In Python, and most other languages, it is not possible to use dashes in variable names. However, in HTTP headers,
dashes
are used by convention.

This can be handled in two ways

1. `convert_underscores` which defaults to true will convert underscores to dashes in the headers. This is default
   behavior so you will need to set it to false if you want to keep the underscores.
2. Another escape hatch is to use the `alias` keyword.

## Embed keys in request body

By design `RequestModel` will ignore the outer key in the request body. This is done to map a pydantic `BaseModel` to
the top level
of the request body. If you want to include the outer key, you can use the `embed` variable in the Body parameter.

```python
from typing import Annotated

from pydantic import BaseModel
from requestmodel import RequestModel
from requestmodel.params import Body


class PersonForm(BaseModel):
    name: str
    age: int


class PersonFormRequest(RequestModel[PersonForm]):
    method = "POST"
    url = "/api/v1/person/create"
    # a BaseModel will be added to the body by default
    body: PersonForm
    # so this is the same as above
    body: Annotated[PersonForm, Body()]
    # remember to set the response_model to the object instead of annotating its type
    response_model = PersonForm
```

In the above example the name and age paremeters will be sent as the top level of the request body.

```json
{
  "name": "John",
  "age": 42
}
```

If you want to include the outer key, you can use the `embed` variable in the Body parameter.

```python
    body: Annotated[Form, Body(embed=True)]
```

Age and name will not be nested in the body key

```json
{
  "body": {
    "name": "John",
    "age": 42
  }
}
```

## Python types as request and responses

Most API's will return a dictionary to embed a list response behind a key to provide more meta information, in example for providing information about the pagination object.

However, sometimes you will encounter API's that return a list directly. To enable serialization of these responses you need to make use of a TypeAdapter provided by pydantic.

```python
from pydantic import BaseModel
from pydantic import TypeAdapter
from requestmodel import IteratorRequestModel

class Person(BaseModel):
    name: str
    age: int


PersonList = TypeAdapter[list[Person]]

# as the generic type, use the plain python type
class PersonRequest(IteratorRequestModel[list[Person]]):
    method = "GET"
    url = "/api/v1/persons"
    limit: int = 10
    offset: int = 0

    # to make serialization possible, use the TypeAdapter as the response_model
    response_model = PersonList

    def next_from_response(self, response: list[Person]) -> bool:
        self.offset += self.limit
        return len(response) >= self.limit

```
