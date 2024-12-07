import copy
import io
import zipfile

from base64 import b64decode, b64encode
from typing import Optional, Union

from .base_types import Iterable


class File:
    def __init__(self, name: str, content: Optional[Union[str, bytes]] = None):
        self.name = name

        # Let's keep content attribute internally encoded as bytes.
        if isinstance(content, str):
            self.content = content.encode()
        elif isinstance(content, bytes):
            self.content = content
        else:
            self.content = b""

    def __str__(self):
        return self.content.decode(errors="backslashreplace")


class Filesystem:
    def __init__(
        self,
        content: Optional[Union[str, bytes, File, Iterable[File], "Filesystem"]] = None,
    ):
        self.files: list[File] = []

        if isinstance(content, (bytes, str)):
            if isinstance(content, bytes):
                zip_bytes = content
            else:
                zip_bytes = b64decode(content.encode())

            with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zip_file:
                for file_name in zip_file.namelist():
                    with zip_file.open(file_name) as fp:
                        self.files.append(File(file_name, fp.read()))
        elif isinstance(content, Iterable):
            self.files = list(content)
        elif isinstance(content, File):
            self.files = [content]
        elif isinstance(content, Filesystem):
            self.files = copy.deepcopy(content.files)
        elif content is None:
            pass
        else:
            raise ValueError(
                "Unsupported type for content argument. Expected "
                "one of str, bytes, File, Iterable[File], or Filesystem, "
                f"got {type(content)}."
            )

    def __repr__(self) -> str:
        content_encoded = b64encode(self.encode()).decode()
        return f"{self.__class__.__name__}(content={content_encoded!r})"

    def encode(self) -> bytes:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for file in self.files:
                zip_file.writestr(file.name, file.content)
        return zip_buffer.getvalue()

    def to_dict(self) -> dict:
        """Pack the Filesystem object to a dictionary."""
        return {"filesystem": str(self)}

    @staticmethod
    def from_dict(filesystem_dict: dict) -> "Filesystem":
        """Create a Filesystem object from dictionary."""
        return Filesystem(filesystem_dict.get("filesystem"))

    def __str__(self) -> str:
        """Create string representation of Filesystem object."""
        return b64encode(self.encode()).decode()

    def __iter__(self):
        return iter(self.files)
