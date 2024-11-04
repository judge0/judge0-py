import os

from .api import async_execute, execute, sync_execute, wait
from .clients import CE, Client, EXTRA_CE
from .retry import MaxRetries, MaxWaitTime, RegularPeriodRetry
from .submission import Submission

__all__ = [
    Client,
    *CE,
    *EXTRA_CE,
    Submission,
    RegularPeriodRetry,
    MaxRetries,
    MaxWaitTime,
    async_execute,
    sync_execute,
    execute,
    wait,
]


def _create_default_ce_client():
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except:  # noqa: E722
        pass

    client = None
    for client_class in CE:
        api_key = os.getenv(client_class.API_KEY_ENV)
        if api_key is not None:
            client = client_class(api_key)

    # TODO: If client is none, instantiate the default client.

    globals()["judge0_default_client"] = client


_create_default_ce_client()
