import logging
from collections.abc import Iterator

import fetcherror
from client import APIClient
from config import ENDPOINT_PATH

logger = logging.getLogger(__name__)


def _fetch_page(client: APIClient, page: int, page_size: int) -> list[dict]:
    response = client.get(
        ENDPOINT_PATH,
        params={"per_page": page_size, "page": page, "by_country": "United States"},
    )
    content_type = response.headers.get("content-type")
    if "application/json" not in content_type:
        raise fetcherror.InvalidResponseError(f"invalid content-type: {content_type}")
    return response.json()


def fetch_all(client: APIClient, page_size: int) -> Iterator[list[dict]]:
    page: int = 1
    while True:
        response = _fetch_page(client, page, page_size)
        yield response
        if not response or len(response) < page_size:
            break
        page += 1
