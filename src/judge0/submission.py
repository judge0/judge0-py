from base64 import b64decode, b64encode
from dataclasses import dataclass
from typing import Union

ENCODED_REQUEST_FIELDS = {
    "source_code",
    "additional_files",
    "stdin",
    "expected_output",
}
ENCODED_RESPONSE_FIELDS = {"stdout", "stderr", "compile_output"}
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


@dataclass
class Submission:
    """
    Stores a representation of a Submission to/from Judge0.
    """

    def __init__(
        self,
        source_code,
        language_id,
        additional_files,
        *,
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
        self.language_id = language_id
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
        self.token = None
        self.time = None
        self.wall_time = None
        self.memory = None

    def encode(self, text: str) -> str:
        return b64encode(bytes(text, "utf-8")).decode()

    def decode(self, bytes_string: str) -> str:
        return b64decode(bytes_string.encode()).decode()

    def update_extra_request_fields(self, body):
        for field in EXTRA_REQUEST_FIELDS:
            value = getattr(self, field)
            if value is not None:
                body[field] = value

    def set_attributes(self, attributes):
        for attr, value in attributes.items():
            if attr in ENCODED_FIELDS:
                setattr(self, attr, self.decode(value) if value else None)
            else:
                setattr(self, attr, value)


class SingleFileSubmission(Submission):
    def __init__(
        self,
        source_code: str,
        language_id: int,
        **kwargs,
    ):

        super().__init__(source_code, language_id, None, **kwargs)


class MultiFileSubmission(Submission):
    def __init__(
        self,
        additional_files,
        **kwargs,
    ):

        super().__init__(None, 89, additional_files, **kwargs)
