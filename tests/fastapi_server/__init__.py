from fastapi import FastAPI
from fastapi import File
from fastapi import Header
from fastapi import params
from starlette.testclient import TestClient
from typing_extensions import Annotated

from tests.fastapi_server.schema import FileCreateSchema
from tests.fastapi_server.schema import FileUploadResponse
from tests.fastapi_server.schema import PaginatedResponse


app = FastAPI()


@app.post("/files/{path}")
async def create_file(
    path: str,
    name: str,
    file: Annotated[bytes, File()],
    extra_header: Annotated[str, Header()],
) -> FileUploadResponse:
    response = FileUploadResponse(
        file_size=len(file), path=path, name=name, extra_header=extra_header
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


@app.put("/items")
async def create_item(
    data: Annotated[FileCreateSchema, params.Body()]
) -> FileCreateSchema:
    return data


client = TestClient(app)
