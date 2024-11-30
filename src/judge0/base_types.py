from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import IntEnum, auto
from typing import Optional, Sequence, Union

Iterable = Sequence

TestCaseType = Union["TestCase", list, tuple, dict]
TestCases = Iterable[TestCaseType]


@dataclass(frozen=True)
class TestCase:
    input: Optional[str] = None
    expected_output: Optional[str] = None

    @staticmethod
    def from_record(test_case: Optional[TestCaseType] = None) -> "TestCase":
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
    ASSEMBLY = auto()
    BASH = auto()
    BASIC = auto()
    BOSQUE = auto()
    C = auto()
    C3 = auto()
    CLOJURE = auto()
    COBOL = auto()
    COMMON_LISP = auto()
    CPP = auto()
    CPP_CLANG = auto()
    CPP_GCC = auto()
    CPP_TEST = auto()
    CSHARP = auto()
    CSHARP_MONO = auto()
    CSHARP_NET_CORE = auto()
    CSHARP_TEST = auto()
    C_CLANG = auto()
    C_GCC = auto()
    D = auto()
    DART = auto()
    ELIXIR = auto()
    ERLANG = auto()
    EXECUTABLE = auto()
    FORTRAN = auto()
    FSHARP = auto()
    GO = auto()
    GROOVY = auto()
    HASKELL = auto()
    JAVA = auto()
    JAVAFX = auto()
    JAVASCRIPT = auto()
    JAVA_OPENJDK = auto()
    JAVA_TEST = auto()
    KOTLIN = auto()
    LUA = auto()
    MPI_C = auto()
    MPI_CPP = auto()
    MPI_PYTHON = auto()
    MULTI_FILE = auto()
    NIM = auto()
    OBJECTIVE_C = auto()
    OCAML = auto()
    OCTAVE = auto()
    PASCAL = auto()
    PERL = auto()
    PHP = auto()
    PLAIN_TEXT = auto()
    PYTHON = auto()
    PYTHON2 = auto()
    PYTHON2_PYPY = auto()
    PYTHON3 = auto()
    PYTHON3_PYPY = auto()
    PYTHON_FOR_ML = auto()
    PYTHON_PYPY = auto()
    R = auto()
    RUBY = auto()
    RUST = auto()
    SCALA = auto()
    SQLITE = auto()
    SWIFT = auto()
    TYPESCRIPT = auto()
    VISUAL_BASIC = auto()


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
