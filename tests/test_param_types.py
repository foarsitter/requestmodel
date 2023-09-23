from typing import ClassVar
from typing import List
from typing import Type

from fastapi import FastAPI
from fastapi import File
from fastapi import Header
from pydantic import BaseModel
from starlette.testclient import TestClient
from typing_extensions import Annotated

from requestmodel import IteratorRequestModel
from requestmodel import RequestModel


app = FastAPI()


class FileUploadResponse(BaseModel):
    file_size: int
    name: str
    path: str
    x_token: str


class PaginatedResponse(BaseModel):
    items: List[int]
    total: int
    page: int
    size: int


@app.post("/files/{path}")
async def create_file(
    path: str,
    name: str,
    file: Annotated[bytes, File()],
    x_token: Annotated[str, Header()],
) -> FileUploadResponse:
    response = FileUploadResponse(
        file_size=len(file), path=path, name=name, x_token=x_token
    )
    return response


@app.get("/items")
async def get_items(page: int = 1, size: int = 25) -> PaginatedResponse:
    max_items = 100

    end = min(page * size, max_items)
    start = max(0, end - size)

    return PaginatedResponse(
        items=list(range(start, end)), total=100, page=page, size=size
    )


client = TestClient(app)


class FileUploadRequest(RequestModel[FileUploadResponse]):
    method: ClassVar[str] = "POST"
    url: ClassVar[str] = "/files/{path}"
    response_model: ClassVar[Type[FileUploadResponse]] = FileUploadResponse

    path: str
    name: str
    file: Annotated[bytes, File()]
    x_token: Annotated[str, Header()]


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


def test_file_upload() -> None:
    request = FileUploadRequest(name="test", path="test", file=b"test", x_token="test1")

    response = request.send(client)

    assert isinstance(response, FileUploadResponse)
    assert response.name == "test"
    assert response.path == "test"
    assert response.x_token == "test1"
    assert response.file_size == 4


def test_paginated() -> None:
    for response in PaginatedRequest(page=1, size=25).send(client):
        print(response.page)
