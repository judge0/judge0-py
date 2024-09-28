from base64 import b64decode, b64encode

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
        self.source_code = source_code  # stored as bytes internally
        self.language_id = language_id
        self.additional_files = additional_files  # stored as bytes internally

        # Extra pre-execution submission attributes.
        self.compiler_options = compiler_options
        self.command_line_arguments = command_line_arguments
        self.stdin = stdin  # stored as bytes internally
        self.expected_output = expected_output  # stored as bytes internally
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
        self.stdout = None  # stored as bytes internally
        self.stderr = None  # stored as bytes internally
        self.compile_output = None  # stored as bytes internally
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

    def check(self, client, *, fields=None):
        """Check the submission status."""
        headers = {
            "Accept": "application/json",
            # NOTE: Only valid for Sulu clients.
            "Authorization": f"Bearer {client.auth_token}",
        }
        params = {
            "base64_encoded": "true",
        }

        if fields is not None:
            params["fields"] = ",".join(fields)

        resp = client.session.get(
            f"{client.endpoint}/submissions/{self.token}",
            headers=headers,
            params=params,
        )
        resp.raise_for_status()

        self.set_properties(resp.json())

    def submit(self, client):
        headers = {
            "Accept": "application/json",
            # NOTE: Only valid for Sulu clients.
            "Authorization": f"Bearer {client.auth_token}",
        }
        params = {
            "base64_encoded": "true",
            "wait": str(client.wait).lower(),
        }

        body = {
            "source_code": b64encode(self.source_code).decode(),
            "language_id": self.language_id,
        }

        if self.stdin:
            body["stdin"] = b64encode(self.stdin).decode()
        if self.expected_output:
            body["expected_output"] = b64encode(self.expected_output).decode()

        for field in EXTRA_REQUEST_FIELDS:
            value = getattr(self, field)
            if value is not None:
                body[field] = value

        resp = client.session.post(
            f"{client.endpoint}/submissions",
            headers=headers,
            params=params,
            json=body,
        )
        resp.raise_for_status()

        self.set_properties(resp.json())

    def set_properties(self, d):
        for key, value in d.items():
            if key in ENCODED_FIELDS:
                setattr(self, key, b64decode(value.encode()) if value else None)
            else:
                setattr(self, key, value)


class SingleFileSubmission(Submission):
    def __init__(
        self,
        source_code: str = None,
        language_id: int = None,
        additional_files=None,
        **kwargs,
    ):
        if source_code is None:
            raise ValueError(
                "Argument source_code should not be None for SingleFileSubmission."
            )

        if language_id is None:
            raise ValueError(
                "Argument language_id should not be None for SingleFileSubmission."
            )

        super().__init__(source_code, language_id, additional_files, **kwargs)


class MultiFileSubmission(Submission):
    def __init__(
        self,
        source_code: str = None,
        language_id: int = 89,
        additional_files=None,
        **kwargs,
    ):
        if additional_files is None:
            raise ValueError(
                "Argument additional_files should not be None for MultiFileSubmission."
            )

        super().__init__(source_code, language_id, additional_files, **kwargs)
