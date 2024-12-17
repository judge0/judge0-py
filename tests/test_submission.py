from judge0 import run, Status, Submission, wait
from judge0.base_types import LanguageAlias


def test_from_json():
    submission_dict = {
        "source_code": "cHJpbnQoJ0hlbGxvLCBXb3JsZCEnKQ==",
        "language_id": 100,
        "stdin": None,
        "expected_output": None,
        "stdout": "SGVsbG8sIFdvcmxkIQo=",
        "status_id": 3,
        "created_at": "2024-12-09T17:22:55.662Z",
        "finished_at": "2024-12-09T17:22:56.045Z",
        "time": "0.152",
        "memory": 13740,
        "stderr": None,
        "token": "5513d8ca-975b-4499-b54b-342f1952d00e",
        "number_of_runs": 1,
        "cpu_time_limit": "5.0",
        "cpu_extra_time": "1.0",
        "wall_time_limit": "10.0",
        "memory_limit": 128000,
        "stack_limit": 64000,
        "max_processes_and_or_threads": 60,
        "enable_per_process_and_thread_time_limit": False,
        "enable_per_process_and_thread_memory_limit": False,
        "max_file_size": 1024,
        "compile_output": None,
        "exit_code": 0,
        "exit_signal": None,
        "message": None,
        "wall_time": "0.17",
        "compiler_options": None,
        "command_line_arguments": None,
        "redirect_stderr_to_stdout": False,
        "callback_url": None,
        "additional_files": None,
        "enable_network": False,
        "post_execution_filesystem": "UEsDBBQACAAIANyKiVkAAAAAAAAAABYAAAAJABwAc"
        "2NyaXB0LnB5VVQJAANvJ1dncCdXZ3V4CwABBOgDAAAE6AMAACsoyswr0VD3SM3JyddRCM8v"
        "yklRVNcEAFBLBwgynNLKGAAAABYAAABQSwECHgMUAAgACADciolZMpzSyhgAAAAWAAAACQA"
        "YAAAAAAABAAAApIEAAAAAc2NyaXB0LnB5VVQFAANvJ1dndXgLAAEE6AMAAAToAwAAUEsFBg"
        "AAAAABAAEATwAAAGsAAAAAAA==",
        "status": {"id": 3, "description": "Accepted"},
        "language": {"id": 100, "name": "Python (3.12.5)"},
    }

    _ = Submission(**submission_dict)


def test_status_before_and_after_submission(request):
    client = request.getfixturevalue("judge0_ce_client")
    submission = Submission(source_code='print("Hello World!")')

    assert submission.status is None

    client.create_submission(submission)
    client.get_submission(submission)

    assert submission.status.__class__ == Status
    assert submission.status >= Status.IN_QUEUE


def test_is_done(request):
    client = request.getfixturevalue("judge0_ce_client")
    submission = Submission(source_code='print("Hello World!")')

    assert submission.status is None

    client.create_submission(submission)
    wait(client=client, submissions=submission)

    assert submission.is_done()


def test_language_before_and_after_execution(request):
    client = request.getfixturevalue("judge0_ce_client")
    code = """\
    public class Main {
        public static void main(String[] args) {
            System.out.println("Hello World");
        }
    }
    """

    submission = Submission(
        source_code=code,
        language=LanguageAlias.JAVA,
    )

    assert submission.language == LanguageAlias.JAVA
    run(client=client, submissions=submission)
    assert submission.language == LanguageAlias.JAVA
