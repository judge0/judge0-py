import os
import warnings
from typing import Optional, Union

from .api import async_execute, execute, run, sync_execute, wait
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
from .common import Flavor, Language, Status
from .retry import MaxRetries, MaxWaitTime, RegularPeriodRetry
from .submission import Submission

__all__ = [
    "ATD",
    "ATDJudge0CE",
    "ATDJudge0ExtraCE",
    "Client",
    "Language",
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
    "async_execute",
    "execute",
    "run",
    "sync_execute",
    "wait",
]


def _create_default_client(
    flavor: Flavor,
    preview_client_class: Union[SuluJudge0CE, SuluJudge0ExtraCE],
) -> Optional[Client]:
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

    client = None
    for client_class in client_classes:
        api_key = os.getenv(client_class.API_KEY_ENV)
        if api_key is not None:
            # It is possible for a client to be subscribed to one flavor with
            # API key.
            try:
                client = client_class(api_key)
                break
            except Exception as e:
                warnings.warn(f"Failed to initialize client: {e}")
    else:
        try:
            client = preview_client_class("")
        except Exception as e:
            warnings.warn(f"Failed to initialize preview client: {e}")

    return client


JUDGE0_IMPLICIT_CE_CLIENT = _create_default_client(Flavor.CE, SuluJudge0CE)
JUDGE0_IMPLICIT_EXTRA_CE_CLIENT = _create_default_client(
    Flavor.EXTRA_CE, SuluJudge0ExtraCE
)

CE = Flavor.CE
EXTRA_CE = Flavor.EXTRA_CE

PYTHON = Language.PYTHON
CPP = Language.CPP
JAVA = Language.JAVA
CPP_GCC = Language.CPP_GCC
CPP_CLANG = Language.CPP_CLANG
PYTHON_FOR_ML = Language.PYTHON_FOR_ML
