# _fetch_page()
import httpx
import pytest
import respx

import fetcherror
from client import APIClient
from config import BASE_URL, ENDPOINT_PATH
from fetch import _fetch_page, fetch_all


@respx.mock
def test_fetch_page_happy_path():
    route = respx.get(f"{BASE_URL}{ENDPOINT_PATH}").mock(
        return_value=httpx.Response(200, json=[{"id": 1}])
    )

    with APIClient(BASE_URL) as client:
        data = _fetch_page(client=client, page=1, country="", page_size=10)
    assert data == [{"id": 1}]
    assert route.call_count == 1


@respx.mock
def test_fetch_page_raises_on_incorrect_content():
    route = respx.get(f"{BASE_URL}{ENDPOINT_PATH}").mock(
        return_value=httpx.Response(
            200, headers={"content-type": "plain/text"}, json=[{"id": 1}]
        )
    )

    with APIClient(BASE_URL) as client, pytest.raises(fetcherror.InvalidResponseError):
        _fetch_page(client=client, page=1, country="", page_size=10)
    assert route.call_count == 1


# fetch_all()
@respx.mock
def test_fetch_all_stops_on_empty_page():
    respx.get(f"{BASE_URL}{ENDPOINT_PATH}").mock(
        side_effect=[
            httpx.Response(200, json=[{"id": 1}, {"id": 2}]),
            httpx.Response(200, json=[{"id": 3}]),
            httpx.Response(200, json=[]),
        ]
    )

    with APIClient(BASE_URL) as client:
        breweries = list(fetch_all(client=client, country="United States", page_size=2))

    assert breweries == [[{"id": 1}, {"id": 2}], [{"id": 3}]]

    @respx.mock
    def test_fetch_all_stops_on_invalid_country():
        route = respx.get(f"{BASE_URL}{ENDPOINT_PATH}").mock()

        with APIClient(BASE_URL) as client, pytest.raises(ValueError):
            fetch_all(client=client, country="US", page_size=10)
        assert route.call_count == 0
