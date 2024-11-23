import os

from .api import (
    async_execute,
    async_run,
    execute,
    get_client,
    run,
    sync_execute,
    sync_run,
    wait,
)
from .base_types import Flavor, Language, LanguageAlias, Status, TestCase
from .clients import (
    ATD,
    ATDJudge0CE,
    ATDJudge0ExtraCE,
    Client,
    Rapid,
    RapidJudge0CE,
    RapidJudge0ExtraCE,
    Sulu,
    SuluJudge0CE,
    SuluJudge0ExtraCE,
)
from .filesystem import File, Filesystem
from .retry import MaxRetries, MaxWaitTime, RegularPeriodRetry
from .submission import Submission

__all__ = [
    "ATD",
    "ATDJudge0CE",
    "ATDJudge0ExtraCE",
    "Client",
    "File",
    "Filesystem",
    "Language",
    "LanguageAlias",
    "MaxRetries",
    "MaxWaitTime",
    "Rapid",
    "RapidJudge0CE",
    "RapidJudge0ExtraCE",
    "RegularPeriodRetry",
    "Status",
    "Submission",
    "Sulu",
    "SuluJudge0CE",
    "SuluJudge0ExtraCE",
    "TestCase",
    "async_execute",
    "execute",
    "get_client",
    "async_run",
    "sync_run",
    "run",
    "sync_execute",
    "wait",
]

JUDGE0_IMPLICIT_CE_CLIENT = None
JUDGE0_IMPLICIT_EXTRA_CE_CLIENT = None


def _get_implicit_client(flavor: Flavor) -> Client:
    global JUDGE0_IMPLICIT_CE_CLIENT, JUDGE0_IMPLICIT_EXTRA_CE_CLIENT

    # Implicit clients are already set.
    if flavor == Flavor.CE and JUDGE0_IMPLICIT_CE_CLIENT is not None:
        return JUDGE0_IMPLICIT_CE_CLIENT
    if flavor == Flavor.EXTRA_CE and JUDGE0_IMPLICIT_EXTRA_CE_CLIENT is not None:
        return JUDGE0_IMPLICIT_EXTRA_CE_CLIENT

    from .clients import CE, EXTRA_CE

    try:
        from dotenv import load_dotenv

        load_dotenv()
    except:  # noqa: E722
        pass

    if flavor == Flavor.CE:
        client_classes = CE
    else:
        client_classes = EXTRA_CE

    # Try to find one of the predefined keys JUDGE0_{SULU,RAPID,ATD}_API_KEY
    # in environment variables.
    client = None
    for client_class in client_classes:
        api_key = os.getenv(client_class.API_KEY_ENV)
        if api_key is not None:
            client = client_class(api_key)
            break

    # If we didn't find any of the possible predefined keys, initialize
    # the preview Sulu client based on the flavor.
    if client is None:
        if flavor == Flavor.CE:
            client = SuluJudge0CE()
        else:
            client = SuluJudge0ExtraCE()

    if flavor == Flavor.CE:
        JUDGE0_IMPLICIT_CE_CLIENT = client
    else:
        JUDGE0_IMPLICIT_EXTRA_CE_CLIENT = client

    return client


CE = Flavor.CE
EXTRA_CE = Flavor.EXTRA_CE

PYTHON = LanguageAlias.PYTHON
CPP = LanguageAlias.CPP
JAVA = LanguageAlias.JAVA
CPP_GCC = LanguageAlias.CPP_GCC
CPP_CLANG = LanguageAlias.CPP_CLANG
PYTHON_FOR_ML = LanguageAlias.PYTHON_FOR_ML
