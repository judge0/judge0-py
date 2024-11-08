from typing import Optional, Union

from .clients import Client
from .common import Flavor
from .data import LANGUAGE_TO_LANGUAGE_ID
from .retry import RegularPeriodRetry, RetryMechanism
from .submission import Submission


def resolve_client(
    client: Optional[Union[Client, Flavor]] = None,
    submissions: Optional[Union[Submission, list[Submission]]] = None,
) -> Union[Client, None]:
    from . import JUDGE0_IMPLICIT_CE_CLIENT, JUDGE0_IMPLICIT_EXTRA_CE_CLIENT

    # User explicitly passed a client.
    if isinstance(client, Client):
        return client

    # User explicitly choose the flavor of the client.
    if isinstance(client, Flavor):
        if client == Flavor.CE:
            return JUDGE0_IMPLICIT_CE_CLIENT
        else:
            return JUDGE0_IMPLICIT_EXTRA_CE_CLIENT

    # client is None and we have to determine a flavor of the client from the
    # submissions and the languages.
    if isinstance(submissions, Submission):
        submissions = [submissions]

    if submissions is not None and len(submissions) == 0:
        raise ValueError("Client cannot be determined from empty submissions argument.")

    if submissions is None:
        raise ValueError(
            "Client cannot be determined from unprovided submissions argument."
        )

    # Check which client supports all languages from the provided submissions.
    languages = [submission.language_id for submission in submissions]

    if JUDGE0_IMPLICIT_CE_CLIENT is not None:
        if all(
            [
                JUDGE0_IMPLICIT_CE_CLIENT.is_language_supported(lang)
                for lang in languages
            ]
        ):
            return JUDGE0_IMPLICIT_CE_CLIENT

    if JUDGE0_IMPLICIT_EXTRA_CE_CLIENT is not None:
        if all(
            [
                JUDGE0_IMPLICIT_EXTRA_CE_CLIENT.is_language_supported(lang)
                for lang in languages
            ]
        ):
            return JUDGE0_IMPLICIT_EXTRA_CE_CLIENT

    raise RuntimeError(
        "Failed to resolve the client from submissions argument."
        "None of the implicit clients supports all languages from the submissions."
        "Please explicitly provide the client argument."
    )


def wait(
    client: Client,
    submissions: Union[Submission, list[Submission]],
    *,
    retry_mechanism: Optional[RetryMechanism] = None,
) -> Union[Submission, list[Submission]]:
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
    client: Optional[Union[Client, Flavor]] = None,
    submissions: Optional[Union[Submission, list[Submission]]] = None,
) -> Union[Submission, list[Submission]]:
    client = resolve_client(client)

    if isinstance(submissions, (list, tuple)):
        return client.create_submissions(submissions)
    else:
        return client.create_submission(submissions)


def sync_execute(
    *,
    client: Optional[Union[Client, Flavor]] = None,
    submissions: Union[Submission, list[Submission], None] = None,
) -> Union[Submission, list[Submission]]:
    client = resolve_client(client, submissions=submissions)
    submissions = async_execute(client=client, submissions=submissions)
    return wait(client, submissions)


execute = sync_execute
run = execute