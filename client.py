import json
import logging
from typing import Any, Self

import httpx
from tenacity import (
	RetryCallState,
	retry,
	retry_if_result,
	stop_after_attempt,
	wait_random_exponential,
)

from config import ENDPOINT_PATH

logger = logging.getLogger(__name__)

SERVER_ERROR_CODES = [500, 502, 503, 504]

# helper functions for retry
def is_retryable_error(exc: BaseException) -> bool:
	if isinstance(exc, httpx.TransportError):
		logger.debug("transport error, will retry: %s", exc)
		return True
	if isinstance(exc, httpx.HTTPStatusError):
		if exc.response.status_code == 429:
			logger.debug("rate limited, will retry: %s", exc.response.status_code)
			return True
		if exc.response.status_code in SERVER_ERROR_CODES:
			logger.warning("server error, will retry: %s", exc.response.status_code)
			return True
	return False

def backoff_time(retry_state: RetryCallState) -> float:
	outcome = retry_state.outcome
	if outcome is not None and outcome.failed:
		exc = outcome.exception()
		if isinstance(exc, httpx.HTTPStatusError):
			retry_after: float = exc.response.headers.get("Retry-After")
			if retry_after:
				logger.info("honoring Retry-After: %ss", retry_after)
				return float(retry_after)
	return wait_random_exponential(max=30)(retry_state)

def retry_exhausted(retry_state: RetryCallState):
	logger.error("retry exhausted after %s attempts", retry_state.attempt_number)
	if retry_state.outcome is None:
			raise RuntimeError("retry exhausted with no outcome recorded")
	exc = retry_state.outcome.exception()
	if exc is None:
			raise RuntimeError("retry exhausted with no captured exception")
	raise exc


class APIClient:
	def __init__(self, base_url: str, timeout: float = 30.0) -> None:
		self._client = httpx.Client(base_url=base_url, timeout=timeout)

	def __enter__(self) -> Self:
		return self

	def __exit__(self, exc_type, exc_val, exc_tb) -> None:
		self._client.close()
		
# get method wrapped with tenacity's retry only on transient errors
	@retry(
			stop=stop_after_attempt(5),
			wait=backoff_time,
			retry=retry_if_result(is_retryable_error),
			retry_error_callback=retry_exhausted,
			)
	def _get(self, path: str, params: dict[str, Any] | None = None) -> httpx.Response:
		response = self._client.get(path, params=params)
		response.raise_for_status()
		return response

	def fetch_page(self, country: str, page: int, page_size: int = 50, ) -> Any:
		response = self._get(ENDPOINT_PATH, params={
			"per_page": page_size, 
			"page": page, 
			"by_country": country
			})
		response_json = json.loads(response.content)
		return response_json

