import httpx
import pytest
import respx
import tenacity

from client import (
    APIClient,
    backoff_time,
    is_retryable_error,
    retry_exhausted,
)
from config import BASE_URL, ENDPOINT_PATH
from fetch import _fetch_page


# helper functions for creating mocks
def make_status_error(
    status_code: int, headers: dict | None = None
) -> httpx.HTTPStatusError:
    request = httpx.Request("GET", BASE_URL)
    response = httpx.Response(status_code, headers=headers, request=request)
    return httpx.HTTPStatusError("error", request=request, response=response)


def make_retry_state(
    attempt_number: int = 0, exc: BaseException | None = None
) -> tenacity.RetryCallState:
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
    ],
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


# _get()
@respx.mock
def test_get_retries_on_503_then_succeeds(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda *args, **kwargs: None)
    route = respx.get(f"{BASE_URL}{ENDPOINT_PATH}").mock(
        side_effect=[
            httpx.Response(503),
            httpx.Response(200, json=[]),
        ]
    )
    with APIClient(BASE_URL) as client:
        data = _fetch_page(client=client, page=1, country="", page_size=10)
    assert data == []
    assert route.call_count == 2


@respx.mock
def test_get_does_not_retry_on_404():
    route = respx.get(f"{BASE_URL}{ENDPOINT_PATH}").mock(
        return_value=httpx.Response(404)
    )

    with APIClient(BASE_URL) as client, pytest.raises(httpx.HTTPStatusError):
        _fetch_page(client=client, page=1, country="", page_size=10)
    assert route.call_count == 1


@respx.mock
def test_get_gives_up_after_max_attempts(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda *args, **kwargs: None)
    route = respx.get(f"{BASE_URL}{ENDPOINT_PATH}").mock(
        return_value=httpx.Response(503)
    )

    with APIClient(BASE_URL) as client, pytest.raises(httpx.HTTPStatusError):
        _fetch_page(client=client, page=1, country="", page_size=10)
    assert route.call_count == 5
