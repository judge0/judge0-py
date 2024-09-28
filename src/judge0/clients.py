from abc import abstractmethod
from typing import Union

import requests

from .base import DEFAULT_SULU_CE_ENDPOINT, DEFAULT_SULU_EXTRA_CE_ENDPOINT


class BaseSuluClient:

    def __init__(
        self,
        *,
        endpoint: Union[str, None] = None,
        auth_token: Union[str, None] = None,
        wait: bool = False,
    ):
        if endpoint is None:
            endpoint = self.default_endpoint

        self.endpoint = endpoint
        self.auth_token = auth_token
        self.wait = wait
        self.session = requests.Session()

    def get_about(self) -> dict:
        # TODO: Potentially think about caching the successful return.
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        r = requests.get(f"{self.endpoint}/about", headers=headers)
        r.raise_for_status()
        self.session.headers.update(headers)
        return r.json()

    def get_config_info(self) -> dict:
        # TODO: Potentially think about caching the successful return.
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        r = requests.get(f"{self.endpoint}/config_info", headers=headers)
        r.raise_for_status()
        self.session.headers.update(headers)
        return r.json()

    def get_statuses(self) -> list[dict]:
        # TODO: Potentially think about caching the successful return.
        # TODO: Add docs about Status enum.
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        r = requests.get(f"{self.endpoint}/statuses", headers=headers)
        r.raise_for_status()
        self.session.headers.update(headers)
        return r.json()

    def get_languages(
        self, *, language_id: Union[int, None] = None
    ) -> Union[dict, list[dict]]:
        # TODO: Potentially think about caching the successful return.
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        request_url = f"{self.endpoint}/languages"
        if language_id is not None:
            request_url = f"{request_url}/{language_id}"
            headers.update({"Accept": "application/json"})
        r = requests.get(request_url, headers=headers)
        r.raise_for_status()
        self.session.headers.update(headers)
        return r.json()

    @property
    @abstractmethod
    def default_endpoint(self) -> str:
        raise NotImplementedError("Subclasses must define a default endpoint property.")


class SuluCEClient(BaseSuluClient):

    @property
    def default_endpoint(self):
        return DEFAULT_SULU_CE_ENDPOINT


class SuluExtraCEClient(BaseSuluClient):

    @property
    def default_endpoint(self):
        return DEFAULT_SULU_EXTRA_CE_ENDPOINT
