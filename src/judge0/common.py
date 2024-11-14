from base64 import b64decode, b64encode


def encode(text: str) -> str:
    return b64encode(bytes(text, "utf-8")).decode()


def decode(b64_encoded_str: str) -> str:
    return b64decode(b64_encoded_str.encode()).decode(errors="backslashreplace")
