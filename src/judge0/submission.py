import copy
from datetime import datetime
from typing import Optional, Union

from judge0.filesystem import Filesystem

from .base_types import LanguageAlias, Status
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
    # "post_execution_filesystem",
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
    "post_execution_filesystem",
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

Submissions = Union[list["Submission"], tuple["Submission"]]


class Submission:
    """
    Stores a representation of a Submission to/from Judge0.
    """

    def __init__(
        self,
        *,
        source_code: Optional[str] = None,
        language: Union[LanguageAlias, int] = LanguageAlias.PYTHON,
        additional_files=None,
        compiler_options=None,
        command_line_arguments=None,
        stdin=None,
        expected_output=None,
        cpu_time_limit=None,
        cpu_extra_time=None,
        wall_time_limit=None,
        memory_limit=None,
        stack_limit=None,
        max_processes_and_or_threads=None,
        enable_per_process_and_thread_time_limit=None,
        enable_per_process_and_thread_memory_limit=None,
        max_file_size=None,
        redirect_stderr_to_stdout=None,
        enable_network=None,
        number_of_runs=None,
        callback_url=None,
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
        self.stdout = None
        self.stderr = None
        self.compile_output = None
        self.message = None
        self.exit_code = None
        self.exit_signal = None
        self.status = None
        self.created_at = None
        self.finished_at = None
        self.token = ""
        self.time = None
        self.wall_time = None
        self.memory = None
        self.post_execution_filesystem = None

    def set_attributes(self, attributes):
        for attr, value in attributes.items():
            if attr in SKIP_FIELDS:
                continue

            if attr in ENCODED_FIELDS:
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

    def is_done(self) -> bool:
        if self.status is None:
            return False
        else:
            return self.status not in (Status.IN_QUEUE, Status.PROCESSING)

    def pre_execution_copy(self) -> "Submission":
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
