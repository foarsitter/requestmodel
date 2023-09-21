"""Testing the LookupRequest."""
import pytest
from httpx import AsyncClient
from httpx import Client

from tests.locatieserver.models import LookupResponse
from tests.locatieserver.requests import LookupRequest


def test_lookup_request_sync() -> None:
    client = Client(base_url="https://api.pdok.nl/bzk/locatieserver/search/v3_1/")

    request = LookupRequest(id="adr-bf54db721969487ed33ba84d9973c702")

    response: LookupResponse = request.send(client)

    assert response.response.num_found == 1


@pytest.mark.asyncio
async def test_lookup_request_async() -> None:
    client = AsyncClient(base_url="https://api.pdok.nl/bzk/locatieserver/search/v3_1/")

    request = LookupRequest(id="adr-bf54db721969487ed33ba84d9973c702")

    response: LookupResponse = await request.asend(client)

    assert response.response.num_found == 1
