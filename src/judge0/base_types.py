from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import IntEnum
from typing import Optional, Union


TestCases = Union[
    list["TestCase"],
    tuple["TestCase"],
    list[dict],
    tuple[dict],
    list[list],
    list[tuple],
    tuple[list],
    tuple[tuple],
]


@dataclass(frozen=True)
class TestCase:
    # Needed to disable pytest from recognizing it as a class containing different test cases.
    __test__ = False

    input: Optional[str] = None
    expected_output: Optional[str] = None

    @staticmethod
    def from_record(
        test_case: Optional[Union[tuple, list, dict, "TestCase"]] = None
    ) -> "TestCase":
        if isinstance(test_case, (tuple, list)):
            test_case = {
                field: value
                for field, value in zip(("input", "expected_output"), test_case)
            }
        if isinstance(test_case, dict):
            return TestCase(
                input=test_case.get("input", None),
                expected_output=test_case.get("expected_output", None),
            )
        if isinstance(test_case, TestCase) or test_case is None:
            return test_case
        raise ValueError(
            f"Cannot create TestCase object from object of type {type(test_case)}."
        )


class Encodeable(ABC):
    @abstractmethod
    def encode(self) -> bytes:
        pass


@dataclass(frozen=True)
class Language:
    id: int
    name: str


class LanguageAlias(IntEnum):
    PYTHON = 0
    CPP = 1
    JAVA = 2
    CPP_GCC = 3
    CPP_CLANG = 4
    PYTHON_FOR_ML = 5


class Flavor(IntEnum):
    CE = 0
    EXTRA_CE = 1


class Status(IntEnum):
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


@dataclass(frozen=True)
class Config:
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
