from typing import Any
from typing import ClassVar
from typing import Optional
from typing import Type

import pytest
from fastapi import params
from fastapi._compat import field_annotation_is_scalar
from pydantic import BaseModel
from typing_extensions import Annotated
from typing_extensions import get_type_hints

from requestmodel import RequestModel
from requestmodel import get_annotated_type


def test_request_args_for_values() -> None:
    class SimpleResponse(BaseModel):
        data: str

    class SimpleBody(BaseModel):
        data: str

    class ModelWithClassVar(RequestModel[SimpleResponse]):
        url: ClassVar[str] = "test"
        method: ClassVar[str] = "POST"
        response_model: ClassVar[Type[SimpleResponse]] = SimpleResponse
        body: SimpleBody

    x = ModelWithClassVar(body=SimpleBody(data="test"))

    v = x.request_args_for_values()

    assert "url" not in v
    assert "method" not in v
    assert "body" not in v
    assert "response_model" not in v


def test_none_as_query_param_value() -> None:
    """We want to override a value and set it to null"""

    class SimpleResponse(BaseModel):
        data: str

    class ModelWithClassVar(RequestModel[SimpleResponse]):
        url: ClassVar[str] = "test"
        method: ClassVar[str] = "POST"
        response_model: ClassVar[Type[SimpleResponse]] = SimpleResponse
        page: Optional[int]

    x = ModelWithClassVar(page=None)

    v = x.request_args_for_values()

    assert "page" in v[params.Query]


def test_get_annotated_type() -> None:
    class SimpleResponse(BaseModel):
        data: str

    class AnnotatedType(RequestModel[Any]):
        a: Annotated[str, params.Query()]
        b: Annotated[SimpleResponse, params.Body()]
        c: Annotated[str, params.Header()]

        # a BaseModel cannot be used as query param so should be placed in the body
        d: SimpleResponse
        e: Annotated[SimpleResponse, params.Body()]

        # this should race an exception
        f: Annotated[SimpleResponse, params.Path()]
        g: Annotated[SimpleResponse, params.Query()]

    hints = get_type_hints(AnnotatedType, include_extras=True)

    assert isinstance(get_annotated_type("a", hints["a"]), params.Query)
    assert isinstance(get_annotated_type("b", hints["b"]), params.Body)
    assert isinstance(get_annotated_type("c", hints["c"]), params.Header)
    assert isinstance(get_annotated_type("d", hints["d"]), params.Body)
    assert isinstance(get_annotated_type("e", hints["e"]), params.Body)

    with pytest.raises(ValueError, match="can only be a scalar"):
        assert isinstance(get_annotated_type("f", hints["f"]), params.Path)

    with pytest.raises(ValueError, match="can only be a scalar"):
        assert isinstance(get_annotated_type("g", hints["g"]), params.Query)


def test_field_annotation_is_scalar():
    class SimpleResponse(BaseModel):
        data: str

    assert field_annotation_is_scalar(SimpleResponse) is False
    assert field_annotation_is_scalar(str) is True
    assert field_annotation_is_scalar(Annotated[str, params.Path()]) is True
    assert field_annotation_is_scalar(Annotated[SimpleResponse, params.Path()]) is True
