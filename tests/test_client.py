import httpx
import pytest
import tenacity

from client import (
	backoff_time,
	is_retryable_error,
	retry_exhausted,
)

BASE_URL = "https://api.example.test"

# helper functions for creating mocks
def make_status_error(status_code: int, headers: dict | None = None) -> httpx.HTTPStatusError:
	request = httpx.Request("GET", BASE_URL)
	response = httpx.Response(status_code, headers=headers, request=request)
	return httpx.HTTPStatusError("error", request=request, response=response)

def make_retry_state(attempt_number: int = 0, exc: BaseException | None = None) -> tenacity.RetryCallState:
	retry_state = tenacity.RetryCallState(tenacity.Retrying(), None, (), {})
	retry_state.attempt_number = attempt_number
	if exc is not None:
		retry_state.set_exception((type(exc), exc, None))
	return retry_state

# is_retryable_error()
@pytest.mark.parametrize(
	"exc, expected",
	[
		(httpx.ConnectError("test"), True),
		(httpx.ReadTimeout("test"), True),
		(make_status_error(429), True),
		(make_status_error(503), True),
		(make_status_error(500), True),
		(make_status_error(404), False),
		(make_status_error(400), False),
		(ValueError("unrelated"), False),
	],
)
def test_is_retryable_error(exc: BaseException, expected: bool) -> None:
	assert is_retryable_error(exc) is expected

# backoff_time()
@pytest.mark.parametrize(
		"exc, deterministic, expected",
		[
			(make_status_error(429, headers={"Retry-After": "5"}), True, 5),
			(make_status_error(503), False, None),

		]
)
def test_backoff_time(exc: BaseException, deterministic: bool, expected: float | None):
	retry_state = make_retry_state(0, exc)
	result = backoff_time(retry_state)

	if deterministic and expected != None:
		assert isinstance(result, float) and result == expected
	else:
		assert isinstance(result, float) and result >= 0 

# retry_exhausted()
def test_log_retry_exhausted_reraises():
	exc = make_status_error(503)
	retry_state = make_retry_state(5, exc)

	with pytest.raises(httpx.HTTPStatusError) as exc_info:
		retry_exhausted(retry_state)
	assert exc_info.value is exc
 
 
def test_log_retry_exhausted_logs_error(caplog):
	exc = make_status_error(503)
	retry_state = make_retry_state(5, exc)

	with caplog.at_level("ERROR"), pytest.raises(httpx.HTTPStatusError):
		retry_exhausted(retry_state)
	assert any("retry exhausted" in record.message for record in caplog.records)
 
 
def test_log_retry_exhausted_raises_if_no_outcome():
	retry_state = make_retry_state(5, None)

	with pytest.raises(RuntimeError, match="no outcome recorded"):
		retry_exhausted(retry_state)