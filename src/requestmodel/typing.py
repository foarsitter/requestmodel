from typing import TypeVar, Dict, Type, Any

from pydantic import BaseModel
from pydantic.fields import FieldInfo

ResponseType = TypeVar("ResponseType", bound=BaseModel)
RequestArgs = Dict[Type[FieldInfo], Dict[str, Any]]
