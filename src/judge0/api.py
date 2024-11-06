from typing import Optional, Union

from .clients import Client
from .common import Flavor
from .retry import RegularPeriodRetry, RetryMechanism
from .submission import Submission


def _resolve_client(client: Union[Client, Flavor]) -> Client:
    if not isinstance(client, Flavor):
        return client

    if client == Flavor.CE:
        from . import JUDGE0_IMPLICIT_CE_CLIENT

        client = JUDGE0_IMPLICIT_CE_CLIENT
    else:
        from . import JUDGE0_IMPLICIT_EXTRA_CE_CLIENT

        client = JUDGE0_IMPLICIT_EXTRA_CE_CLIENT

    return client


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
    client: Union[Client, Flavor] = Flavor.CE,
    submissions: Union[Submission, list[Submission], None] = None,
) -> Union[Submission, list[Submission]]:
    client = _resolve_client(client)

    if isinstance(submissions, (list, tuple)):
        return client.create_submissions(submissions)
    else:
        return client.create_submission(submissions)


def sync_execute(
    *,
    client: Union[Client, Flavor] = Flavor.CE,
    submissions: Union[Submission, list[Submission], None] = None,
) -> Union[Submission, list[Submission]]:
    client = _resolve_client(client)
    submissions = async_execute(client=client, submissions=submissions)
    return wait(client, submissions)


execute = sync_execute
run = execute
