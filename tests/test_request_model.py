import typing
from typing import Any, List, Dict
from typing import ClassVar
from typing import Optional
from typing import Type

import pytest
from fastapi import params, Query
from fastapi._compat import (
    field_annotation_is_scalar,
    field_annotation_is_sequence,
    field_annotation_is_complex,
)
from httpx import Client
from pydantic import BaseModel, ValidationError
from typing_extensions import Annotated, get_origin, get_args
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


def test_annotated_type():
    class SimpleResponse(BaseModel):
        data: str

    assert isinstance(
        get_annotated_type("w", Annotated[List[str], params.Query()]), params.Query
    )
    assert isinstance(get_annotated_type("w", List[str]), params.Query)

    with pytest.raises(
        ValueError,
        match="`x` annotated as Query can only be a scalar, not a `SimpleResponse`",
    ):
        get_annotated_type("x", Annotated[SimpleResponse, params.Query()])

    with pytest.raises(
        ValueError,
        match="`y` annotated as Query can only be a scalar, not a `Dict`",
    ):
        get_annotated_type("y", Annotated[Dict[str, str], params.Query()])


def test_field_annotation_is_sequence() -> None:
    class SimpleResponse(BaseModel):
        data: str

    assert field_annotation_is_sequence(str) is False
    assert field_annotation_is_sequence(List[str]) is True
    assert field_annotation_is_sequence(SimpleResponse) is False


def test_field_annotation_is_scalar() -> None:
    class SimpleResponse(BaseModel):
        data: str

    # assert field_annotation_is_complex(SimpleResponse) is True
    assert field_annotation_is_scalar(Annotated[SimpleResponse, params.Path()]) is True

    # assert field_annotation_is_scalar(SimpleResponse) is False
    # assert field_annotation_is_scalar(str) is True
    # assert field_annotation_is_scalar(Annotated[str, params.Path()]) is True
    # assert field_annotation_is_scalar(Annotated[SimpleResponse, params.Path()]) is True


def test_field_annotation_with_constraints() -> None:
    class SimpleRequest(RequestModel[Any]):
        url = "test"
        method = "test"
        data: Annotated[str, params.Query(min_length=8, max_length=10)]

    with pytest.raises(
        ValidationError, match="String should have at least 8 characters"
    ):
        SimpleRequest(data="test")


def test_field_unified_body() -> None:
    class SimpleRequest(RequestModel[Any]):
        url = "test"
        method = "test"
        query_list: Annotated[List[int], params.Query()]
        data_str: Annotated[str, params.Body()]
        data_int: Annotated[int, params.Body()]
        data_list: Annotated[List[int], params.Body()]
        data_dict: Annotated[Dict[str, int], params.Body(embed=True)]

    data = dict(
        data_str="test", data_int=1, data_list=[0, 1, 2], data_dict={"key": 1925}
    )

    r = SimpleRequest(**data, query_list=[1, 2, 3])

    x = r.request_args_for_values()

    assert x == {
        params.Query: {"query_list": [1, 2, 3]},
        params.Cookie: {},
        params.Header: {},
        params.Path: {},
        params.File: {},
        params.Body: data,
    }


def test_get_origin():
    assert get_origin(str) is None
    assert get_origin(List[str]) is list
    assert get_origin(Annotated[List[str], params.Query()]) is Annotated
    assert get_origin(Annotated[str, params.Query()]) is Annotated


def test_get_args():
    assert get_args(List[str]) == (str,)
    p = get_args(Annotated[List[str], params.Query()])
    assert p[0] == List[str]
    assert isinstance(p[1], params.Query)
