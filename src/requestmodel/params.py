from typing import Any

from pydantic.fields import FieldInfo


class Param(FieldInfo):  # type: ignore[misc]
    pass


class Body(Param):  # type: ignore[misc]
    def __init__(self, embed: bool = False, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.embed = embed


class Cookie(Param):  # type: ignore[misc]
    pass


class File(Param):  # type: ignore[misc]
    pass


class Header(Param):  # type: ignore[misc]
    def __init__(self, convert_underscores: bool = True, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.convert_underscores = convert_underscores


class Path(Param):  # type: ignore[misc]
    pass


class Query(Param):  # type: ignore[misc]
    pass
