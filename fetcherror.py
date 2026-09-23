class FetchError(Exception):
    """Base class for expected failures while fetching data."""


class RequestFailedError(FetchError):
    """HTTP or network failure, after retries."""


class InvalidResponseError(FetchError):
    """The server answered, but not with what we expected."""
