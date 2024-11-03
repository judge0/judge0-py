from typing import Iterable, Optional, Union

import requests

from .retry import RegularPeriodRetry, RetryMechanism

from .submission import Submission


class Client:
    def __init__(self, endpoint, auth_headers) -> None:
        self.endpoint = endpoint
        self.auth_headers = auth_headers
        try:
            self.languages = {lang["id"]: lang for lang in self.get_languages()}
        except Exception:
            raise RuntimeError("Client authentication failed.")

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

    def is_language_supported(self, language_id: int) -> bool:
        return language_id in self.languages

    def create_submission(self, submission: Submission) -> Submission:
        # Check if submission contains supported language.
        if not self.is_language_supported(language_id=submission.language_id):
            raise RuntimeError(
                f"Client {type(self).__name__} does not support language with "
                f"id {submission.language_id}!"
            )

        params = {
            "base64_encoded": "true",
            "wait": "false",
        }

        body = submission.to_dict()

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

    def create_submissions(self, submissions: list[Submission]) -> list[Submission]:
        # Check if all submissions contain supported language.
        for submission in submissions:
            if not self.is_language_supported(language_id=submission.language_id):
                raise RuntimeError(
                    f"Client {type(self).__name__} does not support language with "
                    f"id {submission.language_id}!"
                )

        submissions_body = [submission.to_dict() for submission in submissions]

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
        submissions: list[Submission],
        *,
        fields: Union[str, Iterable[str], None] = None,
    ) -> list[Submission]:
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

    def create_submissions(self, submissions: list[Submission]) -> list[Submission]:
        self._update_endpoint_header(self.DEFAULT_CREATE_SUBMISSIONS_ENDPOINT)
        return super().create_submissions(submissions)

    def get_submissions(
        self,
        submissions: list[Submission],
        *,
        fields: Union[str, Iterable[str], None] = None,
    ) -> list[Submission]:
        self._update_endpoint_header(self.DEFAULT_GET_SUBMISSIONS_ENDPOINT)
        return super().get_submissions(submissions, fields=fields)


class ATDJudge0ExtraCE(ATD):
    DEFAULT_ENDPOINT: str = "https://judge0-extra-ce.proxy-production.allthingsdev.co"
    DEFAULT_HOST: str = "Judge0-Extra-CE.allthingsdev.co"

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

    def create_submissions(self, submissions: list[Submission]) -> list[Submission]:
        self._update_endpoint_header(self.DEFAULT_CREATE_SUBMISSIONS_ENDPOINT)
        return super().create_submissions(submissions)

    def get_submissions(
        self,
        submissions: list[Submission],
        *,
        fields: Union[str, Iterable[str], None] = None,
    ) -> list[Submission]:
        self._update_endpoint_header(self.DEFAULT_GET_SUBMISSIONS_ENDPOINT)
        return super().get_submissions(submissions, fields=fields)


class Rapid(Client):
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

    def __init__(self, api_key):
        super().__init__(
            self.DEFAULT_ENDPOINT,
            self.DEFAULT_HOST,
            api_key,
        )


class RapidJudge0ExtraCE(Rapid):
    DEFAULT_ENDPOINT: str = "https://judge0-extra-ce.p.rapidapi.com"
    DEFAULT_HOST: str = "judge0-extra-ce.p.rapidapi.com"

    def __init__(self, api_key):
        super().__init__(
            self.DEFAULT_ENDPOINT,
            self.DEFAULT_HOST,
            api_key,
        )


class Sulu(Client):
    def __init__(self, endpoint, api_key):
        self.api_key = api_key
        super().__init__(endpoint, {"Authorization": f"Bearer {api_key}"})


class SuluJudge0CE(Sulu):
    DEFAULT_ENDPOINT: str = "https://judge0-ce.p.sulu.sh"

    def __init__(self, api_key):
        super().__init__(self.DEFAULT_ENDPOINT, api_key=api_key)


class SuluJudge0ExtraCE(Sulu):
    DEFAULT_ENDPOINT: str = "https://judge0-extra-ce.p.sulu.sh"

    def __init__(self, api_key):
        super().__init__(self.DEFAULT_ENDPOINT, api_key=api_key)


def wait(
    *,
    client: Optional[Client] = None,
    submissions: Union[Submission, list[Submission], None] = None,
    retry_mechanism: Optional[RetryMechanism] = None,
) -> Union[Submission, list[Submission]]:
    if client is None:
        from . import judge0_default_client

        if judge0_default_client is None:
            raise RuntimeError(
                "Client is not set. Please explicitly set the client argument "
                "or make sure that one of the implemented client's API keys "
                "is set as an environment variable."
            )
        else:
            client = judge0_default_client

    if retry_mechanism is None:
        retry_mechanism = RegularPeriodRetry()

    if not isinstance(submissions, (list, tuple)):
        submissions_to_check = {
            submission.token: submission for submission in [submissions]
        }
    else:
        submissions_to_check = {
            submission.token: submission for submission in submissions
        }

    while len(submissions_to_check) > 0 and not retry_mechanism.is_done():
        client.get_submissions(submissions_to_check.values())
        for token in list(submissions_to_check):
            submission = submissions_to_check[token]
            if submission.is_done():
                submissions_to_check.pop(token)

        # Don't wait if there is no submissions to check for anymore.
        if len(submissions_to_check) == 0:
            break

        retry_mechanism.wait()
        retry_mechanism.step()

    return submissions


def async_execute(
    *,
    client: Optional[Client] = None,
    submissions: Union[Submission, list[Submission], None] = None,
) -> Union[Submission, list[Submission]]:
    if client is None:
        from . import judge0_default_client

        if judge0_default_client is None:
            raise RuntimeError(
                "Client is not set. Please explicitly set the client argument "
                "or make sure that one of the implemented client's API keys "
                "is set as an environment variable."
            )
        else:
            client = judge0_default_client

    if isinstance(submissions, (list, tuple)):
        return client.create_submissions(submissions)
    else:
        return client.create_submission(submissions)


def sync_execute(
    *,
    client: Optional[Client] = None,
    submissions: Union[Submission, list[Submission], None] = None,
) -> Union[Submission, list[Submission]]:
    submissions = async_execute(client=client, submissions=submissions)
    return wait(client=client, submissions=submissions)


def execute(
    *,
    client: Optional[Client] = None,
    submissions: Union[Submission, list[Submission], None] = None,
) -> Union[Submission, list[Submission]]:
    return sync_execute(client=client, submissions=submissions)
