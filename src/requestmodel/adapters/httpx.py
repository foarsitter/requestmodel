from typing import Any

from httpx import Request
from httpx._client import BaseClient

from requestmodel.adapters.base import BaseAdapter
from requestmodel.model import RequestModel

from .. import params


class HTTPXAdapter(BaseAdapter):
    name = "httpx"

    def transform(self, client: BaseClient, model: RequestModel[Any]) -> Request:
        request_args = model.request_args_for_values()

        headers = request_args[params.Header]
        body = request_args[params.Body]

        is_json_request = "json" in headers.get("content-type", "")

        r = Request(
            method=model.method,
            url=client._merge_url(model.url.format(**request_args[params.Path])),
            params=request_args[params.Query],
            headers=headers,
            cookies=request_args[params.Cookie],
            files=request_args[params.File],
            data=body if not is_json_request else None,
            json=body if is_json_request else None,
        )

        return r
