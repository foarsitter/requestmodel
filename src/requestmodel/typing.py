from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

from pydantic import BaseModel
from pydantic import TypeAdapter
from pydantic.fields import FieldInfo


ResponseType = TypeVar(
    "ResponseType",
    bound=Union[BaseModel, TypeAdapter[List[BaseModel]], List[BaseModel]],
)
RequestArgs = Dict[Type[FieldInfo], Dict[str, Any]]
