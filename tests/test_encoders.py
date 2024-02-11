from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import PurePath

from requestmodel.fastapi import jsonable_encoder


class XEnum(str, Enum):
    a = "a"
    b = "b"


@dataclass
class XDataclass:
    a: str
    b: int


def test_encoder_by_type() -> None:
    assert jsonable_encoder(XEnum.a) == "a"
    assert jsonable_encoder(XEnum.b) == "b"
    assert jsonable_encoder(PurePath("syz")) == "syz"
    assert jsonable_encoder(XDataclass(a="a", b=1)) == {"a": "a", "b": 1}
    assert jsonable_encoder(datetime(2020, 1, 1, 1, 1, 1)) == "2020-01-01T01:01:01"
    assert jsonable_encoder({"xyz": "abc"}) == {"xyz": "abc"}
