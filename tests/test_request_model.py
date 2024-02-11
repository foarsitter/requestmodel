from typing import Any
from typing import ClassVar
from typing import Dict
from typing import List
from typing import Optional
from typing import Type

import pytest
from fastapi._compat import field_annotation_is_scalar
from fastapi._compat import field_annotation_is_sequence
from pydantic import BaseModel
from pydantic import ValidationError
from typing_extensions import Annotated
from typing_extensions import get_args
from typing_extensions import get_origin
from typing_extensions import get_type_hints

from requestmodel import RequestModel
from requestmodel import params
from requestmodel.utils import get_annotated_type


class SimpleResponse(BaseModel):
    data: str


class SimpleBody(BaseModel):
    data: str


class ModelWithClassVar(RequestModel[SimpleResponse]):
    url: ClassVar[str] = "test"
    method: ClassVar[str] = "POST"
    response_model: ClassVar[Type[SimpleResponse]] = SimpleResponse
    body: SimpleBody
    header_underscore: Annotated[
        str, params.Header(convert_underscores=False, alias="X_Test")
    ]
    header: Annotated[str, params.Header(convert_underscores=False, alias="X-Scored")]
    excluded: Annotated[str, params.Header(exclude=True)]


class ModelWithClassVar2(RequestModel[SimpleResponse]):
    url: ClassVar[str] = "test"
    method: ClassVar[str] = "POST"
    response_model: ClassVar[Type[SimpleResponse]] = SimpleResponse
    page: Optional[int]


def test_request_args_for_values() -> None:
    header_value = "test"
    x = ModelWithClassVar(
        body=SimpleBody(data="test"),
        header_underscore=header_value,
        header=header_value + "2",
        excluded="not present in the output",
    )

    v = x.request_args_for_values()

    assert "url" not in v
    assert "method" not in v
    assert "body" not in v
    assert "response_model" not in v


def test_none_as_query_param_value() -> None:
    """We want to override a value and set it to null"""

    x = ModelWithClassVar2(page=None)

    v = x.request_args_for_values()

    assert "page" in v[params.Query]


class AnnotatedType(RequestModel[SimpleResponse]):
    a: Annotated[str, params.Query()]
    b: Annotated[SimpleResponse, params.Body()]
    c: Annotated[str, params.Header()]

    # a BaseModel cannot be used as query param so should be placed in the body
    d: SimpleResponse
    e: Annotated[SimpleResponse, params.Body()]

    # this should race an exception
    f: Annotated[SimpleResponse, params.Path()]
    g: Annotated[SimpleResponse, params.Query()]


def test_get_annotated_type() -> None:
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


def test_annotated_type() -> None:
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
        match="`y` annotated as Query can only be a scalar, not a `(.)ict`",
    ):
        get_annotated_type("y", Annotated[Dict[str, str], params.Query()])


def test_field_annotation_is_sequence() -> None:
    assert field_annotation_is_sequence(str) is False
    assert field_annotation_is_sequence(List[str]) is True
    assert field_annotation_is_sequence(SimpleResponse) is False


def test_field_annotation_is_scalar() -> None:
    assert field_annotation_is_scalar(Annotated[SimpleResponse, params.Path()]) is True

    assert field_annotation_is_scalar(SimpleResponse) is False
    assert field_annotation_is_scalar(str) is True
    assert field_annotation_is_scalar(Annotated[str, params.Path()]) is True
    assert field_annotation_is_scalar(Annotated[SimpleResponse, params.Path()]) is True


class SimpleRequest(RequestModel[SimpleResponse]):
    url: ClassVar[str] = "test"
    method: ClassVar[str] = "test"
    data: Annotated[str, params.Query(min_length=8, max_length=10)]


class SimpleRequest2(RequestModel[SimpleResponse]):
    url: ClassVar[str] = "test"
    method: ClassVar[str] = "test"
    query_list: Annotated[List[int], params.Query()]
    data_str: Annotated[str, params.Body()]
    data_int: Annotated[int, params.Body()]
    data_list: Annotated[List[int], params.Body()]
    data_dict: Annotated[Dict[str, int], params.Body(embed=True)]
    response_model: ClassVar[Type[SimpleResponse]] = SimpleResponse


def test_field_annotation_with_constraints() -> None:
    with pytest.raises(
        ValidationError, match="String should have at least 8 characters"
    ):
        SimpleRequest(data="test")


def test_field_unified_body() -> None:
    data: Dict[str, Any] = dict(
        data_str="test", data_int=1, data_list=[0, 1, 2], data_dict={"key": 1925}
    )

    r = SimpleRequest2(query_list=[1, 2, 3], **data)

    x = r.request_args_for_values()

    assert x == {
        params.Query: {"query_list": [1, 2, 3]},
        params.Cookie: {},
        params.Header: {},
        params.Path: {},
        params.File: {},
        params.Body: data,
    }


def test_get_origin() -> None:
    assert get_origin(str) is None
    assert get_origin(List[str]) is list
    assert get_origin(Annotated[List[str], params.Query()]) is Annotated
    assert get_origin(Annotated[str, params.Query()]) is Annotated


def test_get_args() -> None:
    assert get_args(List[str]) == (str,)
    p = get_args(Annotated[List[str], params.Query()])
    assert p[0] == List[str]
    assert isinstance(p[1], params.Query)
