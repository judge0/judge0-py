from typing import Iterable, Union

import requests

from .base_types import Config, Language, LanguageAlias
from .data import LANGUAGE_TO_LANGUAGE_ID
from .submission import Submission, Submissions


class Client:
    API_KEY_ENV = "JUDGE0_API_KEY"
    DEFAULT_MAX_SUBMISSION_BATCH_SIZE = 20
    ENABLED_BATCHED_SUBMISSIONS = True
    EFFECTIVE_SUBMISSION_BATCH_SIZE = (
        DEFAULT_MAX_SUBMISSION_BATCH_SIZE if ENABLED_BATCHED_SUBMISSIONS else 1
    )

    def __init__(self, endpoint, auth_headers) -> None:
        self.endpoint = endpoint
        self.auth_headers = auth_headers

        try:
            self.languages = [Language(**lang) for lang in self.get_languages()]
            self.config = Config(**self.get_config_info())
        except Exception as e:
            raise RuntimeError(
                f"Authentication failed. Visit {self.HOME_URL} to get or review your authentication credentials."
            ) from e

    def get_about(self) -> dict:
        r = requests.get(
            f"{self.endpoint}/about",
            headers=self.auth_headers,
        )
        r.raise_for_status()
        return r.json()

    def get_config_info(self) -> dict:
        r = requests.get(
            f"{self.endpoint}/config_info",
            headers=self.auth_headers,
        )
        r.raise_for_status()
        return r.json()

    def get_language(self, language_id) -> dict:
        request_url = f"{self.endpoint}/languages/{language_id}"
        r = requests.get(request_url, headers=self.auth_headers)
        r.raise_for_status()
        return r.json()

    def get_languages(self) -> list[dict]:
        request_url = f"{self.endpoint}/languages"
        r = requests.get(request_url, headers=self.auth_headers)
        r.raise_for_status()
        return r.json()

    def get_statuses(self) -> list[dict]:
        r = requests.get(
            f"{self.endpoint}/statuses",
            headers=self.auth_headers,
        )
        r.raise_for_status()
        return r.json()

    @property
    def version(self):
        if not hasattr(self, "_version"):
            _version = self.get_about()["version"]
            setattr(self, "_version", _version)
        return self._version

    def get_language_id(self, language: Union[LanguageAlias, int]) -> int:
        """Get language id for the corresponding language alias for the client."""
        if isinstance(language, LanguageAlias):
            supported_language_ids = LANGUAGE_TO_LANGUAGE_ID[self.version]
            language = supported_language_ids.get(language, -1)
        return language

    def is_language_supported(self, language: Union[LanguageAlias, int]) -> bool:
        """Check if language is supported by the client."""
        language_id = self.get_language_id(language)
        return any(language_id == lang.id for lang in self.languages)

    def create_submission(self, submission: Submission) -> Submission:
        # Check if the client supports the language specified in the submission.
        if not self.is_language_supported(language=submission.language):
            raise RuntimeError(
                f"Client {type(self).__name__} does not support language with "
                f"id {submission.language}!"
            )

        params = {
            "base64_encoded": "true",
            "wait": "false",
        }

        body = submission.as_body(self)

        resp = requests.post(
            f"{self.endpoint}/submissions",
            json=body,
            params=params,
            headers=self.auth_headers,
        )
        resp.raise_for_status()

        submission.set_attributes(resp.json())

        return submission

    def get_submission(
        self,
        submission: Submission,
        *,
        fields: Union[str, Iterable[str], None] = None,
    ) -> Submission:
        """Check the submission status."""

        params = {
            "base64_encoded": "true",
        }

        if isinstance(fields, str):
            fields = [fields]

        if fields is not None:
            params["fields"] = ",".join(fields)
        else:
            params["fields"] = "*"

        resp = requests.get(
            f"{self.endpoint}/submissions/{submission.token}",
            params=params,
            headers=self.auth_headers,
        )
        resp.raise_for_status()

        submission.set_attributes(resp.json())

        return submission

    def create_submissions(self, submissions: Submissions) -> Submissions:
        # Check if all submissions contain supported language.
        for submission in submissions:
            if not self.is_language_supported(language=submission.language):
                raise RuntimeError(
                    f"Client {type(self).__name__} does not support language "
                    f"{submission.language}!"
                )

        submissions_body = [submission.as_body(self) for submission in submissions]

        resp = requests.post(
            f"{self.endpoint}/submissions/batch",
            headers=self.auth_headers,
            params={"base64_encoded": "true"},
            json={"submissions": submissions_body},
        )
        resp.raise_for_status()

        for submission, attrs in zip(submissions, resp.json()):
            submission.set_attributes(attrs)

        return submissions

    def get_submissions(
        self,
        submissions: Submissions,
        *,
        fields: Union[str, Iterable[str], None] = None,
    ) -> Submissions:
        params = {
            "base64_encoded": "true",
        }

        if isinstance(fields, str):
            fields = [fields]

        if fields is not None:
            params["fields"] = ",".join(fields)
        else:
            params["fields"] = "*"

        tokens = ",".join(submission.token for submission in submissions)
        params["tokens"] = tokens

        resp = requests.get(
            f"{self.endpoint}/submissions/batch",
            params=params,
            headers=self.auth_headers,
        )
        resp.raise_for_status()

        for submission, attrs in zip(submissions, resp.json()["submissions"]):
            submission.set_attributes(attrs)

        return submissions


class ATD(Client):
    API_KEY_ENV = "JUDGE0_ATD_API_KEY"

    def __init__(self, endpoint, host_header_value, api_key):
        self.api_key = api_key
        super().__init__(
            endpoint,
            {
                "x-apihub-host": host_header_value,
                "x-apihub-key": api_key,
            },
        )

    def _update_endpoint_header(self, header_value):
        self.auth_headers["x-apihub-endpoint"] = header_value


class ATDJudge0CE(ATD):
    DEFAULT_ENDPOINT: str = "https://judge0-ce.proxy-production.allthingsdev.co"
    DEFAULT_HOST: str = "Judge0-CE.allthingsdev.co"
    HOME_URL: str = (
        "https://www.allthingsdev.co/apimarketplace/judge0-ce/66b683c8b7b7ad054eb6ff8f"
    )

    DEFAULT_ABOUT_ENDPOINT: str = "01fc1c98-ceee-4f49-8614-f2214703e25f"
    DEFAULT_CONFIG_INFO_ENDPOINT: str = "b7aab45d-5eb0-4519-b092-89e5af4fc4f3"
    DEFAULT_LANGUAGE_ENDPOINT: str = "a50ae6b1-23c1-40eb-b34c-88bc8cf2c764"
    DEFAULT_LANGUAGES_ENDPOINT: str = "03824deb-bd18-4456-8849-69d78e1383cc"
    DEFAULT_STATUSES_ENDPOINT: str = "c37b603f-6f99-4e31-a361-7154c734f19b"
    DEFAULT_CREATE_SUBMISSION_ENDPOINT: str = "6e65686d-40b0-4bf7-a12f-1f6d033c4473"
    DEFAULT_GET_SUBMISSION_ENDPOINT: str = "b7032b8b-86da-40b4-b9d3-b1f5e2b4ee1e"
    DEFAULT_CREATE_SUBMISSIONS_ENDPOINT: str = "402b857c-1126-4450-bfd8-22e1f2cbff2f"
    DEFAULT_GET_SUBMISSIONS_ENDPOINT: str = "e42f2a26-5b02-472a-80c9-61c4bdae32ec"

    def __init__(self, api_key):
        super().__init__(
            self.DEFAULT_ENDPOINT,
            self.DEFAULT_HOST,
            api_key,
        )

    def get_about(self) -> dict:
        self._update_endpoint_header(self.DEFAULT_ABOUT_ENDPOINT)
        return super().get_about()

    def get_config_info(self) -> dict:
        self._update_endpoint_header(self.DEFAULT_CONFIG_INFO_ENDPOINT)
        return super().get_config_info()

    def get_language(self, language_id) -> dict:
        self._update_endpoint_header(self.DEFAULT_LANGUAGE_ENDPOINT)
        return super().get_language(language_id)

    def get_languages(self) -> list[dict]:
        self._update_endpoint_header(self.DEFAULT_LANGUAGES_ENDPOINT)
        return super().get_languages()

    def get_statuses(self) -> list[dict]:
        self._update_endpoint_header(self.DEFAULT_STATUSES_ENDPOINT)
        return super().get_statuses()

    def create_submission(self, submission: Submission) -> Submission:
        self._update_endpoint_header(self.DEFAULT_CREATE_SUBMISSION_ENDPOINT)
        return super().create_submission(submission)

    def get_submission(
        self,
        submission: Submission,
        *,
        fields: Union[str, Iterable[str], None] = None,
    ) -> Submission:
        self._update_endpoint_header(self.DEFAULT_GET_SUBMISSION_ENDPOINT)
        return super().get_submission(submission, fields=fields)

    def create_submissions(self, submissions: Submissions) -> Submissions:
        self._update_endpoint_header(self.DEFAULT_CREATE_SUBMISSIONS_ENDPOINT)
        return super().create_submissions(submissions)

    def get_submissions(
        self,
        submissions: Submissions,
        *,
        fields: Union[str, Iterable[str], None] = None,
    ) -> Submissions:
        self._update_endpoint_header(self.DEFAULT_GET_SUBMISSIONS_ENDPOINT)
        return super().get_submissions(submissions, fields=fields)


class ATDJudge0ExtraCE(ATD):
    DEFAULT_ENDPOINT: str = "https://judge0-extra-ce.proxy-production.allthingsdev.co"
    DEFAULT_HOST: str = "Judge0-Extra-CE.allthingsdev.co"
    HOME_URL: str = (
        "https://www.allthingsdev.co/apimarketplace/judge0-extra-ce/66b68838b7b7ad054eb70690"
    )

    DEFAULT_ABOUT_ENDPOINT: str = "1fd631a1-be6a-47d6-bf4c-987e357e3096"
    DEFAULT_CONFIG_INFO_ENDPOINT: str = "46e05354-2a43-436a-9458-5d111456f0ff"
    DEFAULT_LANGUAGE_ENDPOINT: str = "10465a84-2a2c-4213-845f-45e3c04a5867"
    DEFAULT_LANGUAGES_ENDPOINT: str = "774ecece-1200-41f7-a992-38f186c90803"
    DEFAULT_STATUSES_ENDPOINT: str = "a2843b3c-673d-4966-9a14-2e7d76dcd0cb"
    DEFAULT_CREATE_SUBMISSION_ENDPOINT: str = "be2d195e-dd58-4770-9f3c-d6c0fbc2b6e5"
    DEFAULT_GET_SUBMISSION_ENDPOINT: str = "c3a457cd-37a6-4106-97a8-9e60a223abbc"
    DEFAULT_CREATE_SUBMISSIONS_ENDPOINT: str = "c64df5d3-edfd-4b08-8687-561af2f80d2f"
    DEFAULT_GET_SUBMISSIONS_ENDPOINT: str = "5d173718-8e6a-4cf5-9d8c-db5e6386d037"

    def __init__(self, api_key):
        super().__init__(
            self.DEFAULT_ENDPOINT,
            self.DEFAULT_HOST,
            api_key,
        )

    def get_about(self) -> dict:
        self._update_endpoint_header(self.DEFAULT_ABOUT_ENDPOINT)
        return super().get_about()

    def get_config_info(self) -> dict:
        self._update_endpoint_header(self.DEFAULT_CONFIG_INFO_ENDPOINT)
        return super().get_config_info()

    def get_language(self, language_id) -> dict:
        self._update_endpoint_header(self.DEFAULT_LANGUAGE_ENDPOINT)
        return super().get_language(language_id)

    def get_languages(self) -> list[dict]:
        self._update_endpoint_header(self.DEFAULT_LANGUAGES_ENDPOINT)
        return super().get_languages()

    def get_statuses(self) -> list[dict]:
        self._update_endpoint_header(self.DEFAULT_STATUSES_ENDPOINT)
        return super().get_statuses()

    def create_submission(self, submission: Submission) -> Submission:
        self._update_endpoint_header(self.DEFAULT_CREATE_SUBMISSION_ENDPOINT)
        return super().create_submission(submission)

    def get_submission(
        self,
        submission: Submission,
        *,
        fields: Union[str, Iterable[str], None] = None,
    ) -> Submission:
        self._update_endpoint_header(self.DEFAULT_GET_SUBMISSION_ENDPOINT)
        return super().get_submission(submission, fields=fields)

    def create_submissions(self, submissions: Submissions) -> Submissions:
        self._update_endpoint_header(self.DEFAULT_CREATE_SUBMISSIONS_ENDPOINT)
        return super().create_submissions(submissions)

    def get_submissions(
        self,
        submissions: Submissions,
        *,
        fields: Union[str, Iterable[str], None] = None,
    ) -> Submissions:
        self._update_endpoint_header(self.DEFAULT_GET_SUBMISSIONS_ENDPOINT)
        return super().get_submissions(submissions, fields=fields)


class Rapid(Client):
    API_KEY_ENV = "JUDGE0_RAPID_API_KEY"

    def __init__(self, endpoint, host_header_value, api_key):
        self.api_key = api_key
        super().__init__(
            endpoint,
            {
                "x-rapidapi-host": host_header_value,
                "x-rapidapi-key": api_key,
            },
        )


class RapidJudge0CE(Rapid):
    DEFAULT_ENDPOINT: str = "https://judge0-ce.p.rapidapi.com"
    DEFAULT_HOST: str = "judge0-ce.p.rapidapi.com"
    HOME_URL: str = "https://rapidapi.com/judge0-official/api/judge0-ce"

    def __init__(self, api_key):
        super().__init__(
            self.DEFAULT_ENDPOINT,
            self.DEFAULT_HOST,
            api_key,
        )


class RapidJudge0ExtraCE(Rapid):
    DEFAULT_ENDPOINT: str = "https://judge0-extra-ce.p.rapidapi.com"
    DEFAULT_HOST: str = "judge0-extra-ce.p.rapidapi.com"
    HOME_URL: str = "https://rapidapi.com/judge0-official/api/judge0-extra-ce"

    def __init__(self, api_key):
        super().__init__(
            self.DEFAULT_ENDPOINT,
            self.DEFAULT_HOST,
            api_key,
        )


class Sulu(Client):
    API_KEY_ENV = "JUDGE0_SULU_API_KEY"

    def __init__(self, endpoint, api_key=None):
        self.api_key = api_key
        super().__init__(
            endpoint,
            {"Authorization": f"Bearer {api_key}"} if api_key else None,
        )


class SuluJudge0CE(Sulu):
    DEFAULT_ENDPOINT: str = "https://judge0-ce.p.sulu.sh"
    HOME_URL: str = "https://sparkhub.sulu.sh/apis/judge0/judge0-ce/readme"

    def __init__(self, api_key=None):
        super().__init__(self.DEFAULT_ENDPOINT, api_key)


class SuluJudge0ExtraCE(Sulu):
    DEFAULT_ENDPOINT: str = "https://judge0-extra-ce.p.sulu.sh"
    HOME_URL: str = "https://sparkhub.sulu.sh/apis/judge0/judge0-extra-ce/readme"

    def __init__(self, api_key=None):
        super().__init__(self.DEFAULT_ENDPOINT, api_key)


CE = [RapidJudge0CE, SuluJudge0CE, ATDJudge0CE]
EXTRA_CE = [RapidJudge0ExtraCE, SuluJudge0ExtraCE, ATDJudge0ExtraCE]
