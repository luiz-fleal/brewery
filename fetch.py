import logging
from collections.abc import Iterator

from client import APIClient
from config import AVAILABLE_COUNTRIES, ENDPOINT_PATH

logger = logging.getLogger(__name__)


def _fetch_page(
  client: APIClient, country: str, page: int, page_size: int
) -> list[dict]:
  response = client.get(
    ENDPOINT_PATH, params={"per_page": page_size, "page": page, "by_country": country}
  )
  content_type = response.headers.get("content-type")
  if content_type != "application/json":
    logger.error("incorrect content type received: %s", content_type)
    raise RuntimeError(f"incorrect content type received: {content_type}")
  return response.json()


def fetch_all(client: APIClient, country: str, page_size: int) -> Iterator[list[dict]]:
  if country not in AVAILABLE_COUNTRIES:
    logger.error("invalid country inserted: %s", country)
    raise ValueError(f"invalid country inserted: {country}")
  page: int = 1
  while True:
    response = _fetch_page(client, country, page, page_size)
    yield response
    if not response or len(response) < page_size:
      break
    page += 1
