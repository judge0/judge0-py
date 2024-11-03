import os

from dotenv import load_dotenv

from .clients import (
    async_execute,
    ATDJudge0CE,
    ATDJudge0ExtraCE,
    Client,
    execute,
    RapidJudge0CE,
    RapidJudge0ExtraCE,
    SuluJudge0CE,
    SuluJudge0ExtraCE,
    sync_execute,
    wait,
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


def _create_default_client():
    if globals().get("judge0_default_client") is not None:
        return

    load_dotenv()

    rapid_api_key = os.getenv("JUDGE0_RAPID_API_KEY")
    sulu_api_key = os.getenv("JUDGE0_SULU_API_KEY")
    atd_api_key = os.getenv("JUDGE0_ATD_API_KEY")

    if rapid_api_key is not None:
        client = RapidJudge0CE(api_key=rapid_api_key)
    elif sulu_api_key is not None:
        client = SuluJudge0CE(api_key=sulu_api_key)
    elif atd_api_key is not None:
        client = ATDJudge0CE(api_key=sulu_api_key)
    else:
        client = None

    if client is not None:
        globals()["judge0_default_client"] = client


_create_default_client()
