from typing import Optional, Union

from .clients import Client
from .retry import RegularPeriodRetry, RetryMechanism
from .submission import Submission


def wait(
    submissions: Union[Submission, list[Submission]],
    *,
    client: Optional[Client] = None,
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


execute = sync_execute
