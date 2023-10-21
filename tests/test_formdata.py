from typing import ClassVar
from typing import Dict
from typing import List
from typing import Type

from pydantic import BaseModel

from requestmodel import RequestModel
from tests.flask_server import client


class MyFormData(BaseModel):
    name: str


class FormErrorResponse(BaseModel):
    errors: Dict[str, List[str]]


class FormDataRequestModel(RequestModel[FormErrorResponse]):
    url: ClassVar[str] = "/submit"
    response_model: ClassVar[Type[FormErrorResponse]] = FormErrorResponse
    method: ClassVar[str] = "POST"

    form: MyFormData


def test_form_data_with_errors() -> None:
    request = FormDataRequestModel(form=MyFormData(name=""))

    response = request.send(client)

    assert len(response.errors) == 1
    assert "name" in response.errors


def test_form_data() -> None:
    form_request = FormDataRequestModel(form=MyFormData(name="My Name"))

    response = form_request.send(client)

    assert len(response.errors) == 0
