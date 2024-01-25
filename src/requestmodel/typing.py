from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar

from pydantic import BaseModel
from pydantic.fields import FieldInfo


ResponseType = TypeVar("ResponseType", bound=BaseModel)
RequestArgs = Dict[Type[FieldInfo], Dict[str, Any]]
