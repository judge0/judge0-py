import copy
from datetime import datetime
from typing import Any, Optional, Union

from judge0.filesystem import Filesystem

from .base_types import Iterable, LanguageAlias, Status
from .common import decode, encode

ENCODED_REQUEST_FIELDS = {
    "source_code",
    "additional_files",
    "stdin",
    "expected_output",
}
ENCODED_RESPONSE_FIELDS = {
    "stdout",
    "stderr",
    "compile_output",
    "post_execution_filesystem",
}
ENCODED_FIELDS = ENCODED_REQUEST_FIELDS | ENCODED_RESPONSE_FIELDS
EXTRA_REQUEST_FIELDS = {
    "compiler_options",
    "command_line_arguments",
    "cpu_time_limit",
    "cpu_extra_time",
    "wall_time_limit",
    "memory_limit",
    "stack_limit",
    "max_processes_and_or_threads",
    "enable_per_process_and_thread_time_limit",
    "enable_per_process_and_thread_memory_limit",
    "max_file_size",
    "redirect_stderr_to_stdout",
    "enable_network",
    "number_of_runs",
    "callback_url",
}
EXTRA_RESPONSE_FIELDS = {
    "message",
    "exit_code",
    "exit_signal",
    "status",
    "created_at",
    "finished_at",
    "token",
    "time",
    "wall_time",
    "memory",
}
REQUEST_FIELDS = ENCODED_REQUEST_FIELDS | EXTRA_REQUEST_FIELDS
RESPONSE_FIELDS = ENCODED_RESPONSE_FIELDS | EXTRA_RESPONSE_FIELDS
FIELDS = REQUEST_FIELDS | RESPONSE_FIELDS
SKIP_FIELDS = {"language_id", "language", "status_id"}
DATETIME_FIELDS = {"created_at", "finished_at"}
FLOATING_POINT_FIELDS = {
    "cpu_time_limit",
    "cpu_extra_time",
    "time",
    "wall_time",
    "wall_time_limit",
}

Submissions = Iterable["Submission"]


class Submission:
    """
    Stores a representation of a Submission to/from Judge0.

    Parameters
    ----------
    source_code : str, optional
        The source code to be executed.
    language : LanguageAlias or int, optional
        The programming language of the source code. Defaults to `LanguageAlias.PYTHON`.
    additional_files : base64 encoded string, optional
        Additional files that should be available alongside the source code.
        Value of this string should represent the content of a .zip that
        contains additional files. This attribute is required for multi-file
        programs.
    compiler_options : str, optional
        Options for the compiler (i.e. compiler flags).
    command_line_arguments : str, optional
        Command line arguments for the program.
    stdin : str, optional
        Input to be fed via standard input during execution.
    expected_output : str, optional
        The expected output of the program.
    cpu_time_limit : float, optional
        Maximum CPU time allowed for execution, in seconds. Time in which the
        OS assigns the processor to different tasks is not counted. Depends on
        configuration.
    cpu_extra_time : float, optional
        Additional CPU time allowance in case of time extension. Depends on
        configuration.
    wall_time_limit : float, optional
        Maximum wall clock time allowed for execution, in seconds. Depends on
        configuration.
    memory_limit : float, optional
        Maximum memory allocation allowed for the process, in kilobytes.
        Depends on configuration.
    stack_limit : int, optional
        Maximum stack size allowed, in kilobytes. Depends on configuration.
    max_processes_and_or_threads : int, optional
        Maximum number of processes and/or threads program can create. Depends
        on configuration.
    enable_per_process_and_thread_time_limit : bool, optional
        If True, enforces time limits per process/thread. Depends on
        configuration.
    enable_per_process_and_thread_memory_limit : bool, optional
        If True, enforces memory limits per process/thread. Depends on
        configuration.
    max_file_size : int, optional
        Maximum file size allowed for output files, in kilobytes. Depends on
        configuration.
    redirect_stderr_to_stdout : bool, optional
        If True, redirects standard error output to standard output.
    enable_network : bool, optional
        If True, enables network access during execution.
    number_of_runs : int, optional
        Number of times the code should be executed.
    callback_url : str, optional
        URL for a callback to report execution results or status.
    """

    def __init__(
        self,
        *,
        source_code: Optional[str] = None,
        language: Union[LanguageAlias, int] = LanguageAlias.PYTHON,
        additional_files: Optional[str] = None,
        compiler_options: Optional[str] = None,
        command_line_arguments: Optional[str] = None,
        stdin: Optional[str] = None,
        expected_output: Optional[str] = None,
        cpu_time_limit: Optional[float] = None,
        cpu_extra_time: Optional[float] = None,
        wall_time_limit: Optional[float] = None,
        memory_limit: Optional[float] = None,
        stack_limit: Optional[int] = None,
        max_processes_and_or_threads: Optional[int] = None,
        enable_per_process_and_thread_time_limit: Optional[bool] = None,
        enable_per_process_and_thread_memory_limit: Optional[bool] = None,
        max_file_size: Optional[int] = None,
        redirect_stderr_to_stdout: Optional[bool] = None,
        enable_network: Optional[bool] = None,
        number_of_runs: Optional[int] = None,
        callback_url: Optional[str] = None,
    ):
        self.source_code = source_code
        self.language = language
        self.additional_files = additional_files

        # Extra pre-execution submission attributes.
        self.compiler_options = compiler_options
        self.command_line_arguments = command_line_arguments
        self.stdin = stdin
        self.expected_output = expected_output
        self.cpu_time_limit = cpu_time_limit
        self.cpu_extra_time = cpu_extra_time
        self.wall_time_limit = wall_time_limit
        self.memory_limit = memory_limit
        self.stack_limit = stack_limit
        self.max_processes_and_or_threads = max_processes_and_or_threads
        self.enable_per_process_and_thread_time_limit = (
            enable_per_process_and_thread_time_limit
        )
        self.enable_per_process_and_thread_memory_limit = (
            enable_per_process_and_thread_memory_limit
        )
        self.max_file_size = max_file_size
        self.redirect_stderr_to_stdout = redirect_stderr_to_stdout
        self.enable_network = enable_network
        self.number_of_runs = number_of_runs
        self.callback_url = callback_url

        # Post-execution submission attributes.
        self.stdout: Optional[str] = None
        self.stderr: Optional[str] = None
        self.compile_output: Optional[str] = None
        self.message: Optional[str] = None
        self.exit_code: Optional[int] = None
        self.exit_signal: Optional[int] = None
        self.status: Optional[Status] = None
        self.created_at: Optional[datetime] = None
        self.finished_at: Optional[datetime] = None
        self.token: str = ""
        self.time: Optional[float] = None
        self.wall_time: Optional[float] = None
        self.memory: Optional[float] = None
        self.post_execution_filesystem: Optional[Filesystem] = None

    def set_attributes(self, attributes: dict[str, Any]) -> None:
        """Set Submissions attributes while taking into account different
        attribute's types.

        Parameters
        ----------
        attributes : dict
            Key-value pairs of Submission attributes and the corresponding
            value.
        """
        for attr, value in attributes.items():
            if attr in SKIP_FIELDS:
                continue

            if attr in ENCODED_FIELDS and attr not in ("post_execution_filesystem",):
                value = decode(value) if value else None
            elif attr == "status":
                value = Status(value["id"])
            elif attr in DATETIME_FIELDS and value is not None:
                value = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
            elif attr in FLOATING_POINT_FIELDS and value is not None:
                value = float(value)
            elif attr == "post_execution_filesystem":
                value = Filesystem(value)

            setattr(self, attr, value)

    def as_body(self, client: "Client") -> dict:
        """Prepare Submission as a dictionary while taking into account
        the `client`'s restrictions.
        """
        body = {
            "source_code": encode(self.source_code),
            "language_id": client.get_language_id(self.language),
        }

        for field in ENCODED_REQUEST_FIELDS:
            value = getattr(self, field)
            if value is not None:
                body[field] = encode(value)

        for field in EXTRA_REQUEST_FIELDS:
            value = getattr(self, field)
            if value is not None:
                body[field] = value

        return body

    def to_dict(self) -> dict:
        encoded_request_fields = {
            field_name: encode(getattr(self, field_name))
            for field_name in ENCODED_REQUEST_FIELDS
            if getattr(self, field_name) is not None
        }
        extra_request_fields = {
            field_name: getattr(self, field_name)
            for field_name in EXTRA_REQUEST_FIELDS
            if getattr(self, field_name) is not None
        }
        encoded_response_fields = {
            field_name: encode(getattr(self, field_name))
            for field_name in ENCODED_RESPONSE_FIELDS
            if getattr(self, field_name) is not None
        }
        extra_response_fields = {
            field_name: getattr(self, field_name)
            for field_name in EXTRA_RESPONSE_FIELDS
            if getattr(self, field_name) is not None
        }

        submission_dict = (
            encoded_request_fields
            | extra_request_fields
            | encoded_response_fields
            | extra_response_fields
        )

        return submission_dict

    @staticmethod
    def from_dict(submission_dict) -> "Submission":
        submission = Submission()
        submission.set_attributes(submission_dict)
        return submission

    def is_done(self) -> bool:
        """Check if submission is finished processing.

        Submission is considered finished if the submission status is not
        IN_QUEUE and not PROCESSING.
        """
        if self.status is None:
            return False
        else:
            return self.status not in (Status.IN_QUEUE, Status.PROCESSING)

    def pre_execution_copy(self) -> "Submission":
        """Create a deep copy of a submission."""
        new_submission = Submission()
        for attr in REQUEST_FIELDS:
            setattr(new_submission, attr, copy.deepcopy(getattr(self, attr)))
        return new_submission

    def __repr__(self) -> str:
        arguments = ", ".join(f"{field}={getattr(self, field)!r}" for field in FIELDS)
        return f"{self.__class__.__name__}({arguments})"

    def __iter__(self):
        if self.post_execution_filesystem is None:
            return iter([])
        else:
            return iter(self.post_execution_filesystem)
