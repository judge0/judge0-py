import os

import pytest
from dotenv import load_dotenv

from judge0 import clients

load_dotenv()


@pytest.fixture(scope="session")
def judge0_ce_client():
    api_key = os.getenv("JUDGE0_TEST_API_KEY")
    api_key_header = os.getenv("JUDGE0_TEST_API_KEY_HEADER")
    endpoint = os.getenv("JUDGE0_TEST_CE_ENDPOINT")
    client = clients.Client(
        endpoint=endpoint,
        auth_headers={api_key_header: api_key},
    )
    return client


@pytest.fixture(scope="session")
def judge0_extra_ce_client():
    api_key = os.getenv("JUDGE0_TEST_API_KEY")
    api_key_header = os.getenv("JUDGE0_TEST_API_KEY_HEADER")
    endpoint = os.getenv("JUDGE0_TEST_EXTRA_CE_ENDPOINT")
    client = clients.Client(
        endpoint=endpoint,
        auth_headers={api_key_header: api_key},
    )
    return client


@pytest.fixture(scope="session")
def atd_ce_client():
    api_key = os.getenv("JUDGE0_ATD_API_KEY")
    client = clients.ATDJudge0CE(api_key)
    return client


@pytest.fixture(scope="session")
def atd_extra_ce_client():
    api_key = os.getenv("JUDGE0_ATD_API_KEY")
    client = clients.ATDJudge0ExtraCE(api_key)
    return client


@pytest.fixture(scope="session")
def rapid_ce_client():
    api_key = os.getenv("JUDGE0_RAPID_API_KEY")
    client = clients.RapidJudge0CE(api_key)
    return client


@pytest.fixture(scope="session")
def rapid_extra_ce_client():
    api_key = os.getenv("JUDGE0_RAPID_API_KEY")
    client = clients.RapidJudge0ExtraCE(api_key)
    return client


@pytest.fixture(scope="session")
def sulu_ce_client():
    api_key = os.getenv("JUDGE0_SULU_API_KEY")
    client = clients.SuluJudge0CE(api_key)
    return client


@pytest.fixture(scope="session")
def sulu_extra_ce_client():
    api_key = os.getenv("JUDGE0_SULU_API_KEY")
    client = clients.SuluJudge0ExtraCE(api_key)
    return client
