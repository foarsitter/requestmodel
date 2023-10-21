from typing import ClassVar
from typing import List
from typing import Type

from fastapi import File
from fastapi import Header
from fastapi import params
from pydantic import BaseModel
from typing_extensions import Annotated

from requestmodel import RequestModel


class FileUploadResponse(BaseModel):
    file_size: int
    name: str
    path: str
    extra_header: str


class FileCreateSchema(BaseModel):
    name: str
    path: str
    content_type: Annotated[str, params.Header] = "application/json"


class PaginatedResponse(BaseModel):
    items: List[int]
    total: int
    page: int
    size: int


class FileUploadRequest(RequestModel[FileUploadResponse]):
    method: ClassVar[str] = "POST"
    url: ClassVar[str] = "/files/{path}"
    response_model: ClassVar[Type[FileUploadResponse]] = FileUploadResponse

    path: str
    name: str
    file: Annotated[bytes, File()]
    extra_header: Annotated[str, Header()]
