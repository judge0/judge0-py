"""Module containing different utility functions for Judge0 Python SDK."""

from functools import wraps
from http import HTTPStatus

from requests import HTTPError


def is_http_too_many_requests_error(exception: Exception) -> bool:
    return (
        isinstance(exception, HTTPError)
        and exception.response is not None
        and exception.response.status_code == HTTPStatus.TOO_MANY_REQUESTS
    )


def handle_too_many_requests_error_for_preview_client(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except HTTPError as err:
            if is_http_too_many_requests_error(exception=err):
                # If the raised exception is inside the one of the Sulu clients
                # let's check if we are dealing with the implicit client.
                if args:
                    instance = args[0]
                    class_name = instance.__class__.__name__
                    # Check if we are using a preview version of the client.
                    if (
                        class_name in ("SuluJudge0CE", "SuluJudge0ExtraCE")
                        and instance.api_key is None
                    ):
                        raise RuntimeError(
                            "You are using a preview version of the Sulu "
                            "clients and you've hit a rate limit on the preview "
                            f"clients. Visit {instance.HOME_URL} to get or "
                            "review your authentication credentials."
                        ) from err
                else:
                    raise err from None
            else:
                raise err from None
        except Exception as err:
            raise err from None

    return wrapper
