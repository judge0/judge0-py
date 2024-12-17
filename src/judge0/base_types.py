import copy

from dataclasses import dataclass
from enum import IntEnum
from typing import Optional, Protocol, runtime_checkable, Sequence, Union

from pydantic import BaseModel

Iterable = Sequence

TestCaseType = Union["TestCase", list, tuple, dict]
TestCases = Iterable[TestCaseType]


@dataclass(frozen=True)
class TestCase:
    input: Optional[str] = None
    expected_output: Optional[str] = None

    @classmethod
    def from_record(cls, test_case: TestCaseType) -> "TestCase":
        """Create a TestCase from built-in types."""
        if isinstance(test_case, (tuple, list)):
            test_case = {
                field: value
                for field, value in zip(("input", "expected_output"), test_case)
            }
        if isinstance(test_case, dict):
            return cls(
                input=test_case.get("input", None),
                expected_output=test_case.get("expected_output", None),
            )
        if isinstance(test_case, cls):
            return copy.deepcopy(test_case)
        if test_case is None:
            return cls()
        raise ValueError(
            f"Cannot create TestCase object from object of type {type(test_case)}."
        )


@runtime_checkable
class Encodeable(Protocol):
    def encode(self) -> bytes:
        """Serialize the object to bytes."""
        ...


class Language(BaseModel):
    id: int
    name: str
    is_archived: Optional[bool] = None
    source_file: Optional[str] = None
    compile_cmd: Optional[str] = None
    run_cmd: Optional[str] = None


class LanguageAlias(IntEnum):
    """Language enumeration."""

    PYTHON = 0
    CPP = 1
    JAVA = 2
    CPP_GCC = 3
    CPP_CLANG = 4
    PYTHON_FOR_ML = 5


class Flavor(IntEnum):
    """Judge0 flavor enumeration."""

    CE = 0
    EXTRA_CE = 1


class Status(IntEnum):
    """Status enumeration."""

    IN_QUEUE = 1
    PROCESSING = 2
    ACCEPTED = 3
    WRONG_ANSWER = 4
    TIME_LIMIT_EXCEEDED = 5
    COMPILATION_ERROR = 6
    RUNTIME_ERROR_SIGSEGV = 7
    RUNTIME_ERROR_SIGXFSZ = 8
    RUNTIME_ERROR_SIGFPE = 9
    RUNTIME_ERROR_SIGABRT = 10
    RUNTIME_ERROR_NZEC = 11
    RUNTIME_ERROR_OTHER = 12
    INTERNAL_ERROR = 13
    EXEC_FORMAT_ERROR = 14

    def __str__(self):
        return self.name.lower().replace("_", " ").title()


class Config(BaseModel):
    """Client config data."""

    allow_enable_network: bool
    allow_enable_per_process_and_thread_memory_limit: bool
    allow_enable_per_process_and_thread_time_limit: bool
    allowed_languages_for_compile_options: list[str]
    callbacks_max_tries: int
    callbacks_timeout: float
    cpu_extra_time: float
    cpu_time_limit: float
    enable_additional_files: bool
    enable_batched_submissions: bool
    enable_callbacks: bool
    enable_command_line_arguments: bool
    enable_compiler_options: bool
    enable_network: bool
    enable_per_process_and_thread_memory_limit: bool
    enable_per_process_and_thread_time_limit: bool
    enable_submission_delete: bool
    enable_wait_result: bool
    maintenance_mode: bool
    max_cpu_extra_time: float
    max_cpu_time_limit: float
    max_extract_size: int
    max_file_size: int
    max_max_file_size: int
    max_max_processes_and_or_threads: int
    max_memory_limit: int
    max_number_of_runs: int
    max_processes_and_or_threads: int
    max_queue_size: int
    max_stack_limit: int
    max_submission_batch_size: int
    max_wall_time_limit: float
    memory_limit: int
    number_of_runs: int
    redirect_stderr_to_stdout: bool
    stack_limit: int
    submission_cache_duration: float
    use_docs_as_homepage: bool
    wall_time_limit: float
