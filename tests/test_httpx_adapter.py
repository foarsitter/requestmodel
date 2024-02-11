from httpx import Client

from tests.locatieserver.requests import LookupRequest


def test_preserve_header() -> None:
    client = Client(headers={"X-Test": "test"})

    request = LookupRequest(id="test").as_request(client)

    assert request.headers["X-Test"] == "test"
