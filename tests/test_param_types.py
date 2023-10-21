from typing import ClassVar
from typing import Type

from fastapi import Header
from typing_extensions import Annotated

from requestmodel import IteratorRequestModel
from requestmodel import RequestModel
from tests.fastapi_server import client
from tests.fastapi_server.schema import FileCreateSchema
from tests.fastapi_server.schema import FileUploadRequest
from tests.fastapi_server.schema import FileUploadResponse
from tests.fastapi_server.schema import PaginatedResponse


class PaginatedRequest(IteratorRequestModel[PaginatedResponse]):
    method: ClassVar[str] = "GET"
    url: ClassVar[str] = "/items"

    response_model: ClassVar[Type[PaginatedResponse]] = PaginatedResponse

    page: int
    size: int

    def next(self, response: PaginatedResponse) -> bool:
        self.page = response.page + 1
        if self.page * response.size > response.total:
            return False
        return True


class CreateRequest(RequestModel[FileCreateSchema]):
    method: ClassVar[str] = "PUT"
    url: ClassVar[str] = "/items"
    response_model: ClassVar[Type[FileCreateSchema]] = FileCreateSchema

    content_type: Annotated[str, Header()] = "application/json"
    data: FileCreateSchema


def test_file_upload() -> None:
    request = FileUploadRequest(
        name="test", path="test", file=b"test", extra_header="test1"
    )

    response = request.send(client)

    assert isinstance(response, FileUploadResponse)
    assert response.name == "test"
    assert response.path == "test"
    assert response.extra_header == "test1"
    assert response.file_size == 4


def test_paginated() -> None:
    pages = 0
    for _ in PaginatedRequest(page=1, size=25).send(client):
        pages += 1

    assert pages == 4


def test_create() -> None:
    request = CreateRequest(data=FileCreateSchema(name="test", path="test"))

    response = request.send(client)

    assert isinstance(response, FileCreateSchema)
    assert response.name == "test"
    assert response.path == "test"
