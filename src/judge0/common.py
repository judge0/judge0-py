from base64 import b64decode, b64encode
from typing import Union


def encode(content: Union[bytes, str]) -> str:
    if isinstance(content, bytes):
        return b64encode(content).decode()
    if isinstance(content, str):
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
