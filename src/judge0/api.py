from typing import Optional, Union

from .base_types import Flavor, TestCase, LanguageAlias
from .clients import Client
from .retry import RegularPeriodRetry, RetryMechanism
from .submission import Submission

from .filesystem import Filesystem, File
import textwrap


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


def safe_format(f, arg):
    try:
        return (f or "") % (arg or "")
    except TypeError:
        return f or ""


def create_fs(client, submission):
    fs = Filesystem(submission.additional_files)
    language_id = client.get_language_id(submission.language)
    if language_id != LanguageAlias.MULTI_FILE:  # Multi-file program
        language = client.get_language(language_id)
        fs.files.append(File(language["source_file"], submission.source_code))
        fs.files.append(
            File(
                "compile.sh",
                safe_format(language["compile_cmd"], submission.compiler_options),
            )
        )
        fs.files.append(
            File("run.sh", f'{language["run_cmd"]} {submission.command_line_arguments}')
        )
    return fs


def create_submission_with_interactive_producer(
    client, submission, interactive_producer
):
    interactive_producer.command_line_arguments = "/box/stdin.fifo /box/stdout.fifo"

    consumer_fs = create_fs(client, submission)
    producer_fs = create_fs(client, interactive_producer)

    final_fs = Filesystem()
    for f in consumer_fs.files:
        final_fs.files.append(File(f"./consumer/{f.name}", f.content))

    for f in producer_fs.files:
        final_fs.files.append(File(f"./producer/{f.name}", f.content))

    final_fs.files.append(
        File(
            "compile.sh",
            textwrap.dedent(
                """
        cd /box/consumer && bash compile.sh
        cd /box/producer && bash compile.sh
    """
            ),
        )
    )

    final_fs.files.append(
        File(
            "run.sh",
            textwrap.dedent(
                """
        mkfifo /box/stdin.fifo /box/stdout.fifo

        cd /box/consumer
        tee >(bash run.sh 2> /box/user.stderr | tee /box/stdout.fifo /box/user.stdout &> /dev/null) /box/user.stdin < /box/stdin.fifo &> /dev/null &

        cd /box/producer
        bash run.sh < /dev/stdin &
        PRODUCER_PID=$!

        wait $PRODUCER_PID

        rm -f /box/stdin.fifo /box/stdout.fifo
    """
            ),
        )
    )

    return Submission(
        source_code="",
        additional_files=final_fs,
        language=LanguageAlias.MULTI_FILE,
    )


def create_submissions_with_interactive_producer(
    client, submissions, interactive_producer
):
    if isinstance(submissions, Submission):
        return create_submission_with_interactive_producer(
            client, submissions, interactive_producer
        )
    else:
        return [
            create_submission_with_interactive_producer(
                client, submission, interactive_producer
            )
            for submission in submissions
        ]


def _execute(
    *,
    client: Optional[Union[Client, Flavor]] = None,
    submissions: Optional[Union[Submission, list[Submission]]] = None,
    source_code: Optional[str] = None,
    wait_for_result: bool = False,
    test_cases: Optional[Union[TestCase, list[TestCase]]] = None,
    interactive_producer: Optional[Submission] = None,
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

    # TODO: Since kwargs is ignored if submissions argument is provided, maybe
    # use warnings if submission and kwargs are provided?

    # There is no need to check for other cases since we are explicitly
    # checking for submissions and source_code arguments.
    if client is None:
        if isinstance(submissions, list) and len(submissions) == 0:
            raise ValueError("Client cannot be determined from empty submissions.")

    client = resolve_client(client, submissions=submissions)

    if interactive_producer is not None:
        submissions = create_submissions_with_interactive_producer(
            client, submissions, interactive_producer
        )

    all_submissions = create_submissions_from_test_cases(submissions, test_cases)

    # We differentiate between creating a single submission and multiple
    # submissions to be consistent with the API, even though the API
    # allows to create single submission with the same endpoint as for
    # creating the multiple submissions.
    if isinstance(all_submissions, Submission):
        all_submissions = client.create_submission(all_submissions)
    elif len(all_submissions) == 1:
        all_submissions = [client.create_submission(all_submissions[0])]
    else:
        all_submissions = client.create_submissions(all_submissions)

    if wait_for_result:
        all_submissions = wait(client, all_submissions)

    return all_submissions


def async_execute(
    *,
    client: Optional[Union[Client, Flavor]] = None,
    submissions: Optional[Union[Submission, list[Submission]]] = None,
    source_code: Optional[str] = None,
    test_cases: Optional[Union[TestCase, list[TestCase]]] = None,
    interactive_producer: Optional[Submission] = None,
    **kwargs,
) -> Union[Submission, list[Submission]]:
    return _execute(
        client=client,
        submissions=submissions,
        source_code=source_code,
        wait_for_result=False,
        test_cases=test_cases,
        interactive_producer=interactive_producer,
        **kwargs,
    )


def sync_execute(
    *,
    client: Optional[Union[Client, Flavor]] = None,
    submissions: Optional[Union[Submission, list[Submission]]] = None,
    source_code: Optional[str] = None,
    test_cases: Optional[Union[TestCase, list[TestCase]]] = None,
    interactive_producer: Optional[Submission] = None,
    **kwargs,
) -> Union[Submission, list[Submission]]:
    return _execute(
        client=client,
        submissions=submissions,
        source_code=source_code,
        wait_for_result=True,
        test_cases=test_cases,
        interactive_producer=interactive_producer,
        **kwargs,
    )


execute = sync_execute

run = sync_execute
sync_run = sync_execute
async_run = async_execute
