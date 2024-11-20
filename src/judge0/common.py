from base64 import b64decode, b64encode
from itertools import islice
from typing import Union

from .base_types import Encodeable


def encode(content: Union[bytes, str, Encodeable]) -> str:
    if isinstance(content, bytes):
        return b64encode(content).decode()
    if isinstance(content, str):
        return b64encode(content.encode()).decode()
    if isinstance(content, Encodeable):
        return b64encode(content.encode()).decode()
    raise ValueError(f"Unsupported type. Expected bytes or str, got {type(content)}!")


def decode(content: Union[bytes, str]) -> str:
    if isinstance(content, bytes):
        return b64decode(content.decode(errors="backslashreplace")).decode(
            errors="backslashreplace"
        )
    if isinstance(content, str):
        return b64decode(content.encode()).decode(errors="backslashreplace")
    raise ValueError(f"Unsupported type. Expected bytes or str, got {type(content)}!")


def batched(iterable, n):
    """Utility function for batching submissions.

    Adapted from https://docs.python.org/3/library/itertools.html#itertools.batched.
    """
    if n < 1:
        raise ValueError("n must be at least one")
    iterator = iter(iterable)
    while True:
        batch = tuple(islice(iterator, n))
        if not batch:
            break
        yield batch
