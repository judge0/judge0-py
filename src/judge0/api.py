from typing import Iterable, Optional, Union

from .base_types import Flavor, TestCase, TestCases
from .clients import Client
from .common import batched

from .retry import RegularPeriodRetry, RetryMechanism
from .submission import Submission, Submissions


def get_client(flavor: Flavor = Flavor.CE) -> Client:
    from . import _get_implicit_client

    if isinstance(flavor, Flavor):
        return _get_implicit_client(flavor=flavor)
    else:
        raise ValueError(
            "Expected argument flavor to be of of type enum Flavor, "
            f"got {type(flavor)}."
        )


def _resolve_client(
    client: Optional[Union[Client, Flavor]] = None,
    submissions: Optional[Union[Submission, Submissions]] = None,
) -> Client:
    # User explicitly passed a client.
    if isinstance(client, Client):
        return client

    if isinstance(client, Flavor):
        return get_client(client)

    if client is None and isinstance(submissions, list) and len(submissions) == 0:
        raise ValueError("Client cannot be determined from empty submissions.")

    # client is None and we have to determine a flavor of the client from the
    # submissions and the languages.
    if isinstance(submissions, Submission):
        submissions = [submissions]

    # Check which client supports all languages from the provided submissions.
    languages = [submission.language for submission in submissions]

    for flavor in Flavor:
        client = get_client(flavor)
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
    client: Optional[Client] = None,
    submissions: Optional[Union[Submission, Submissions]] = None,
) -> Union[Submission, Submissions]:
    client = _resolve_client(client=client, submissions=submissions)

    if isinstance(submissions, Submission):
        return client.create_submission(submissions)

    result_submissions = []
    for submission_batch in batched(
        submissions, client.config.max_submission_batch_size
    ):
        if len(submission_batch) > 1:
            result_submissions.extend(client.create_submissions(submission_batch))
        else:
            result_submissions.append(client.create_submission(submission_batch[0]))

    return result_submissions


def get_submissions(
    *,
    client: Optional[Client] = None,
    submissions: Optional[Union[Submission, Submissions]] = None,
    fields: Union[str, Iterable[str], None] = None,
) -> Union[Submission, Submissions]:
    client = _resolve_client(client=client, submissions=submissions)

    if isinstance(submissions, Submission):
        return client.get_submission(submissions, fields=fields)

    result_submissions = []
    for submission_batch in batched(
        submissions, client.config.max_submission_batch_size
    ):
        if len(submission_batch) > 1:
            result_submissions.extend(
                client.get_submissions(submission_batch, fields=fields)
            )
        else:
            result_submissions.append(
                client.get_submission(submission_batch[0], fields=fields)
            )

    return result_submissions


def wait(
    *,
    client: Optional[Client] = None,
    submissions: Optional[Union[Submission, Submissions]] = None,
    retry_mechanism: Optional[RetryMechanism] = None,
) -> Union[Submission, Submissions]:
    client = _resolve_client(client, submissions)

    if retry_mechanism is None:
        retry_mechanism = RegularPeriodRetry()

    if isinstance(submissions, Submission):
        submissions_to_check = {
            submission.token: submission for submission in [submissions]
        }
    else:
        submissions_to_check = {
            submission.token: submission for submission in submissions
        }

    while len(submissions_to_check) > 0 and not retry_mechanism.is_done():
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
    submissions: Union[Submission, Submissions],
    test_cases: Optional[Union[TestCase, TestCases]] = None,
):
    """Utility function for creating submissions from the (submission, test_case) pairs.

    The following table contains the return type based on the types of `submissions`
    and `test_cases` arguments:

    | submissions | test_cases | returns     |
    |:------------|:-----------|:------------|
    | Submission  | TestCase   | Submission  |
    | Submission  | TestCases  | Submissions |
    | Submissions | TestCase   | Submissions |
    | Submissions | TestCases  | Submissions |

    """
    if isinstance(submissions, Submission):
        submissions_list = [submissions]
    else:
        submissions_list = submissions

    if isinstance(test_cases, TestCase) or test_cases is None:
        test_cases_list = [test_cases]
    else:
        test_cases_list = test_cases

    test_cases_list = [TestCase.from_record(tc) for tc in test_cases_list]

    all_submissions = []
    for submission in submissions_list:
        for test_case in test_cases_list:
            submission_copy = submission.pre_execution_copy()
            if test_case is not None:
                submission_copy.stdin = test_case.input
                submission_copy.expected_output = test_case.expected_output
            all_submissions.append(submission_copy)

    if isinstance(submissions, Submission) and (
        isinstance(test_cases, TestCase) or test_cases is None
    ):
        return all_submissions[0]
    else:
        return all_submissions


def _execute(
    *,
    client: Optional[Union[Client, Flavor]] = None,
    submissions: Optional[Union[Submission, Submissions]] = None,
    source_code: Optional[str] = None,
    test_cases: Optional[Union[TestCase, TestCases]] = None,
    wait_for_result: bool = False,
    **kwargs,
) -> Union[Submission, Submissions]:
    if submissions is not None and source_code is not None:
        raise ValueError(
            "Both submissions and source_code arguments are provided. "
            "Provide only one of the two."
        )
    if submissions is None and source_code is None:
        raise ValueError("Neither source_code nor submissions argument are provided.")

    if source_code is not None:
        submissions = Submission(source_code=source_code, **kwargs)

    client = _resolve_client(client=client, submissions=submissions)
    all_submissions = create_submissions_from_test_cases(submissions, test_cases)
    all_submissions = create_submissions(client=client, submissions=all_submissions)

    if wait_for_result:
        return wait(client=client, submissions=all_submissions)
    else:
        return all_submissions


def async_execute(
    *,
    client: Optional[Union[Client, Flavor]] = None,
    submissions: Optional[Union[Submission, Submissions]] = None,
    source_code: Optional[str] = None,
    test_cases: Optional[Union[TestCase, TestCases]] = None,
    **kwargs,
) -> Union[Submission, Submissions]:
    return _execute(
        client=client,
        submissions=submissions,
        source_code=source_code,
        test_cases=test_cases,
        wait_for_result=False,
        **kwargs,
    )


def sync_execute(
    *,
    client: Optional[Union[Client, Flavor]] = None,
    submissions: Optional[Union[Submission, Submissions]] = None,
    source_code: Optional[str] = None,
    test_cases: Optional[Union[TestCase, TestCases]] = None,
    **kwargs,
) -> Union[Submission, Submissions]:
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
