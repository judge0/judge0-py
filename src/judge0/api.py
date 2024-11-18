from typing import Optional, Union
from collections.abc import Iterable

from .base_types import Flavor, TestCase
from .clients import Client
from .retry import RegularPeriodRetry, RetryMechanism
from .submission import Submission


def resolve_client(
    *,
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

    if client is None and isinstance(submissions, list) and len(submissions) == 0:
        raise ValueError("Client cannot be determined from empty submissions.")

    # client is None and we have to determine a flavor of the client from the
    # submissions and the languages.
    if isinstance(submissions, Submission):
        submissions = [submissions]

    # Check which client supports all languages from the provided submissions.
    languages = [submission.language for submission in submissions]

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


def create_submissions(
    *,
    client: Optional[Union[Client, Flavor]] = None,
    submissions: Union[Submission, list[Submission]] = None,
) -> Union[Submission, list[Submission]]:
    client = resolve_client(client=client, submissions=submissions)

    MAX_SUBMISSION_BATCH_SIZE = (
        20  # TODO: move to client.config.MAX_SUBMISSION_BATCH_SIZE
    )
    ENABLE_BATCHED_SUBMISSIONS = (
        True  # TODO: Move to client.config.ENABLE_BATCHED_SUBMISSIONS
    )
    actual_batch_size = (
        MAX_SUBMISSION_BATCH_SIZE if ENABLE_BATCHED_SUBMISSIONS else 1
    )  # TODO: Move to client.config.BATCH_SIZE which should be calculated field

    if isinstance(submissions, (list, tuple)):
        if len(submissions) == 0:
            return submissions
        elif len(submissions) == 1:
            return [client.create_submission(submissions[0])]
        else:
            if actual_batch_size > 1:
                submissions_left = client.create_submissions(
                    submissions=submissions[:actual_batch_size]
                )
            else:
                submissions_left = client.create_submission(submissions[0])

            if not isinstance(submissions_left, list):
                submissions_left = [submissions_left]

            submissions_right = create_submissions(
                client=client, submissions=submissions[actual_batch_size:]
            )
            if not isinstance(submissions_right, list):
                submissions_right = [submissions_right]

            return [*submissions_left, *submissions_right]
    else:
        return client.create_submission(submissions)


def get_submissions(
    *,
    client: Optional[Union[Client, Flavor]] = None,
    submissions: Union[Submission, list[Submission]] = None,
) -> Union[Submission, list[Submission]]:
    client = resolve_client(client=client, submissions=submissions)

    MAX_SUBMISSION_BATCH_SIZE = (
        20  # TODO: move to client.config.MAX_SUBMISSION_BATCH_SIZE
    )
    ENABLE_BATCHED_SUBMISSIONS = (
        True  # TODO: Move to client.config.ENABLE_BATCHED_SUBMISSIONS
    )
    actual_batch_size = (
        MAX_SUBMISSION_BATCH_SIZE if ENABLE_BATCHED_SUBMISSIONS else 1
    )  # TODO: Move to client.config.BATCH_SIZE which should be calculated field

    if isinstance(submissions, (list, tuple)):
        if len(submissions) == 0:
            return submissions
        elif len(submissions) == 1:
            return [client.get_submission(submissions[0])]
        else:
            if actual_batch_size > 1:
                submissions_left = client.get_submissions(
                    submissions=submissions[:actual_batch_size]
                )
            else:
                submissions_left = client.get_submission(submissions[0])

            if not isinstance(submissions_left, list):
                submissions_left = [submissions_left]

            submissions_right = get_submissions(
                client=client, submissions=submissions[actual_batch_size:]
            )
            if not isinstance(submissions_right, list):
                submissions_right = [submissions_right]

            return [*submissions_left, *submissions_right]
    else:
        return client.get_submission(submissions)


def wait(
    *,
    client: Optional[Union[Client, Flavor]] = None,
    submissions: Union[Submission, list[Submission]] = None,
    retry_mechanism: Optional[RetryMechanism] = None,
) -> Union[Submission, list[Submission]]:
    client = resolve_client(client=client, submissions=submissions)

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
        # TODO: list should not be needed if use collections.abc.Iterable for isinstance check.
        get_submissions(client=client, submissions=list(submissions_to_check.values()))
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


def create_submissions_from_test_cases(
    submissions: Union[Submission, list[Submission]],
    test_cases: Optional[Union[TestCase, list[TestCase]]] = None,
):
    """Utility function for creating submissions from the (submission, test_case) pairs.

    The following table contains the return type based on the types of `submissions`
    and `test_cases` arguments:

    | submissions      | test_cases     | returns          |
    |:-----------------|:---------------|:-----------------|
    | Submission       | TestCase       | Submission       |
    | Submission       | list[TestCase] | list[Submission] |
    | list[Submission] | TestCase       | list[Submission] |
    | list[Submission] | list[TestCase] | list[Submission] |

    """
    # Let's deal with the simplest cases where no test cases are provided. We
    # return original submissions argument as this gives a user an option
    # to change the original Submission objects, without creating copies of it.
    if test_cases is None or isinstance(test_cases, list) and len(test_cases) == 0:
        return submissions

    if isinstance(submissions, Submission):
        submissions_list = [submissions]
    else:
        submissions_list = submissions

    if isinstance(test_cases, list):
        test_cases_list = test_cases
    else:
        test_cases_list = [test_cases]

    all_submissions = []
    for submission in submissions_list:
        for test_case in test_cases_list:
            submission_copy = submission.copy()
            if test_case is not None:
                submission_copy.stdin = test_case.input
                submission_copy.expected_output = test_case.expected_output
            all_submissions.append(submission_copy)

    if isinstance(submissions, Submission) and not isinstance(test_cases, list):
        return all_submissions[0]
    else:
        return all_submissions


def _execute(
    *,
    client: Optional[Union[Client, Flavor]] = None,
    submissions: Optional[Union[Submission, list[Submission]]] = None,
    source_code: Optional[str] = None,
    wait_for_result: bool = False,
    test_cases: Optional[Union[TestCase, list[TestCase]]] = None,
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

    client = resolve_client(client=client, submissions=submissions)
    all_submissions = create_submissions_from_test_cases(submissions, test_cases)
    all_submissions = create_submissions(client=client, submissions=all_submissions)

    if wait_for_result:
        all_submissions = wait(client=client, submissions=all_submissions)

    return all_submissions


def async_execute(
    *,
    client: Optional[Union[Client, Flavor]] = None,
    submissions: Optional[Union[Submission, list[Submission]]] = None,
    source_code: Optional[str] = None,
    test_cases: Optional[Union[TestCase, list[TestCase]]] = None,
    **kwargs,
) -> Union[Submission, list[Submission]]:
    return _execute(
        client=client,
        submissions=submissions,
        source_code=source_code,
        wait_for_result=False,
        test_cases=test_cases,
        **kwargs,
    )


def sync_execute(
    *,
    client: Optional[Union[Client, Flavor]] = None,
    submissions: Optional[Union[Submission, list[Submission]]] = None,
    source_code: Optional[str] = None,
    test_cases: Optional[Union[TestCase, list[TestCase]]] = None,
    **kwargs,
) -> Union[Submission, list[Submission]]:
    return _execute(
        client=client,
        submissions=submissions,
        source_code=source_code,
        wait_for_result=True,
        test_cases=test_cases,
        **kwargs,
    )


execute = sync_execute

run = sync_execute
sync_run = sync_execute
async_run = async_execute
