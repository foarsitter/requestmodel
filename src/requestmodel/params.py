from pydantic.fields import FieldInfo
from pydantic.fields import _FieldInfoInputs
from typing_extensions import Unpack


class Param(FieldInfo):
    pass


class Body(Param):
    def __init__(self, embed: bool = False, **kwargs: Unpack[_FieldInfoInputs]) -> None:
        super().__init__(**kwargs)
        self.embed = embed


class Cookie(Param):
    pass


class File(Param):
    pass


class Header(Param):
    def __init__(
        self, convert_underscores: bool = True, **kwargs: Unpack[_FieldInfoInputs]
    ) -> None:
        super().__init__(**kwargs)
        self.convert_underscores = convert_underscores


class Path(Param):
    pass


class Query(Param):
    pass
