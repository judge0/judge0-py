from typing import Optional, Union

from .clients import Client
from .common import Flavor
from .retry import RegularPeriodRetry, RetryMechanism
from .submission import Submission


def resolve_client(
    client: Optional[Union[Client, Flavor]] = None,
    submissions: Optional[Union[Submission, list[Submission]]] = None,
) -> Union[Client, None]:
    # User explicitly passed a client.
    if isinstance(client, Client):
        return client

    from . import _get_implicit_client

    # User explicitly choose the flavor of the client.
    if isinstance(client, Flavor):
        return _get_implicit_client(flavor=client)

    # client is None and we have to determine a flavor of the client from the
    # submissions and the languages.
    if isinstance(submissions, Submission):
        submissions = [submissions]

    # Check which client supports all languages from the provided submissions.
    languages = (submission.language_id for submission in submissions)

    for flavor in Flavor:
        client = _get_implicit_client(flavor)
        if client is not None and all(
            (client.is_language_supported(lang) for lang in languages)
        ):
            return client

    raise RuntimeError(
        "Failed to resolve the client from submissions argument. "
        "None of the implicit clients supports all languages from the submissions. "
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

    if isinstance(submissions, (list, tuple)):
        submissions_to_check = {
            submission.token: submission for submission in submissions
        }
    else:
        submissions_to_check = {
            submission.token: submission for submission in [submissions]
        }

    while len(submissions_to_check) > 0 and not retry_mechanism.is_done():
        # We differentiate between getting a single submission and multiple
        # submissions to be consistent with the API, even though the API
        # allows to get single submission with the same endpoint as for getting
        # the multiple submissions.
        if len(submissions_to_check) == 1:
            client.get_submission(*submissions_to_check.values())
        else:
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


def _execute(
    *,
    client: Optional[Union[Client, Flavor]] = None,
    submissions: Optional[Union[Submission, list[Submission]]] = None,
    source_code: Optional[str] = None,
    wait_for_result: bool = False,
    **kwargs,
) -> Union[Submission, list[Submission]]:
    if submissions is not None and source_code is not None:
        raise ValueError(
            "Both submissions and source_code arguments are provided. "
            "Provide only one of the two."
        )
    if submissions is None and source_code is None:
        raise ValueError("Neither source_code nor submissions argument are provided.")

    if source_code is not None:
        submissions = Submission(source_code=source_code, **kwargs)

    # TODO: Since kwargs are ignore if submissions argument is provided, maybe
    # use warnings if submission argument is provided and kwargs are passed?

    # There is no need to check for other cases since we are explicitly
    # checking for submissions and source_code arguments
    if client is None:
        if isinstance(submissions, list) and len(submissions) == 0:
            raise ValueError("Client cannot be determined from empty submissions.")

    client = resolve_client(client, submissions=submissions)

    if isinstance(submissions, (list, tuple)):
        submissions = client.create_submissions(submissions)
    else:
        submissions = client.create_submission(submissions)

    if wait_for_result:
        return wait(client, submissions)
    else:
        return submissions


def async_execute(
    *,
    client: Optional[Union[Client, Flavor]] = None,
    submissions: Optional[Union[Submission, list[Submission]]] = None,
    source_code: Optional[str] = None,
    **kwargs,
) -> Union[Submission, list[Submission]]:
    return _execute(
        client=client,
        submissions=submissions,
        source_code=source_code,
        wait_for_result=False,
        **kwargs,
    )


def sync_execute(
    *,
    client: Optional[Union[Client, Flavor]] = None,
    submissions: Optional[Union[Submission, list[Submission]]] = None,
    source_code: Optional[str] = None,
    **kwargs,
) -> Union[Submission, list[Submission]]:
    return _execute(
        client=client,
        submissions=submissions,
        source_code=source_code,
        wait_for_result=True,
        **kwargs,
    )


execute = sync_execute
run = execute
async_run = async_execute
