import os

import pytest
from dotenv import load_dotenv

from judge0 import clients

load_dotenv()


def test_atd_ce_client():
    api_key = os.getenv("ATD_API_KEY")

    client = clients.ATDJudge0CE(api_key)

    client.get_about()
    client.get_config_info()
    client.get_languages()
    client.get_statuses()


def test_atd_extra_ce_client():
    api_key = os.getenv("ATD_API_KEY")
    client = clients.ATDJudge0ExtraCE(api_key)

    client.get_about()
    client.get_config_info()
    client.get_languages()
    client.get_statuses()


def test_rapid_ce_client():
    api_key = os.getenv("RAPID_API_KEY")
    client = clients.RapidJudge0CE(api_key)

    client.get_about()
    client.get_config_info()
    client.get_languages()
    client.get_statuses()


def test_rapid_extra_ce_client():
    api_key = os.getenv("RAPID_API_KEY")
    client = clients.RapidJudge0ExtraCE(api_key)

    client.get_about()
    client.get_config_info()
    client.get_languages()
    client.get_statuses()


def test_sulu_ce_client():
    api_key = os.getenv("SULU_API_KEY")
    client = clients.SuluJudge0CE(api_key)

    client.get_about()
    client.get_config_info()
    client.get_languages()
    client.get_statuses()


def test_sulu_extra_ce_client():
    api_key = os.getenv("SULU_API_KEY")
    client = clients.SuluJudge0ExtraCE(api_key)

    client.get_about()
    client.get_config_info()
    client.get_languages()
    client.get_statuses()
