import os

from .api import async_execute, execute, sync_execute, wait
from .clients import (
    ATDJudge0CE,
    ATDJudge0ExtraCE,
    Client,
    RapidJudge0CE,
    RapidJudge0ExtraCE,
    SuluJudge0CE,
    SuluJudge0ExtraCE,
)
from .retry import MaxRetries, MaxWaitTime, RegularPeriodRetry
from .submission import Submission

__all__ = [
    ATDJudge0CE,
    ATDJudge0ExtraCE,
    Client,
    RapidJudge0CE,
    RapidJudge0ExtraCE,
    SuluJudge0CE,
    SuluJudge0ExtraCE,
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

    rapid_api_key = os.getenv("JUDGE0_RAPID_API_KEY")
    sulu_api_key = os.getenv("JUDGE0_SULU_API_KEY")
    atd_api_key = os.getenv("JUDGE0_ATD_API_KEY")

    if rapid_api_key is not None:
        client = RapidJudge0CE(api_key=rapid_api_key)
    elif sulu_api_key is not None:
        client = SuluJudge0CE(api_key=sulu_api_key)
    elif atd_api_key is not None:
        client = ATDJudge0CE(api_key=atd_api_key)
    else:
        # TODO: Create SuluJudge0CE with default client.
        client = None

    globals()["judge0_default_client"] = client


_create_default_ce_client()
