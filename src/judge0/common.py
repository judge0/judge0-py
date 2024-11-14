from base64 import b64decode, b64encode
from enum import IntEnum


# TODO: Consider moving enumerations and other possible future types to separate
# module (_types.py).
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


def encode(text: str) -> str:
    return b64encode(bytes(text, "utf-8")).decode()


def decode(b64_encoded_str: str) -> str:
    return b64decode(b64_encoded_str.encode()).decode(errors="backslashreplace")
