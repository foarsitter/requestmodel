from typing import Any
from typing import Dict
from typing import Type


class BaseAdapter:
    """"""

    name: str
    registry: Dict[str, Type["BaseAdapter"]] = {}

    def __init_subclass__(cls, **kwargs: Dict[str, Any]) -> None:
        super().__init_subclass__(**kwargs)
        cls.registry[cls.name] = cls
