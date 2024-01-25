from typing import Optional

from requests import Request
from requests import Response
from requests import Session
from requests.adapters import BaseAdapter

from requestmodel import params
from requestmodel.model import BaseRequestModel
from requestmodel.typing import ResponseType


class RequestsAdapter(BaseAdapter):
    def transform(self, model: BaseRequestModel[ResponseType]) -> Request:
        request_args = model.request_args_for_values()

        headers = request_args[params.Header]
        body = request_args[params.Body]

        is_json_request = "json" in headers.get("content-type", "")

        r = Request(
            method=model.method,
            url=model.url.format(**request_args[params.Path]),
            params=request_args[params.Query],
            headers=headers,
            cookies=request_args[params.Cookie],
            files=request_args[params.File],
            data=body if not is_json_request else None,
            json=body if is_json_request else None,
        )

        return r


class RequestsRequestModel(BaseRequestModel[ResponseType]):
    response: Optional[Response] = None

    def handle_error(self, response: Response) -> None:
        response.raise_for_status()

    def as_request(self) -> Request:
        """Transform the properties of the object into a request"""

        adapter = RequestsAdapter()
        return adapter.transform(self)

    def send(self, client: Session) -> ResponseType:
        """Send the request synchronously"""
        r = self.as_request()
        self.response = client.send(r.prepare())
        self.handle_error(self.response)
        return self.response_model.model_validate(self.response.json())
