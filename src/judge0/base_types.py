from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import IntEnum
from typing import Optional


@dataclass(frozen=True)
class TestCase:
    # Needed to disable pytest from recognizing it as a class containing different test cases.
    __test__ = False

    input: Optional[str] = None
    expected_output: Optional[str] = None


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
