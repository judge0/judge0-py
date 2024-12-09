import copy
import io
import zipfile

from base64 import b64decode, b64encode
from typing import Optional, Union

from pydantic import BaseModel

from .base_types import Iterable


class File(BaseModel):
    name: str
    content: Optional[Union[str, bytes]] = None

    def __init__(self, **data):
        super().__init__(**data)
        # Let's keep content attribute internally encoded as bytes.
        if isinstance(self.content, str):
            self.content = self.content.encode()
        elif isinstance(self.content, bytes):
            self.content = self.content
        else:
            self.content = b""

    def __str__(self):
        return self.content.decode(errors="backslashreplace")


class Filesystem(BaseModel):
    files: list[File] = []

    def __init__(self, **data):
        content = data.pop("content", None)
        super().__init__(**data)
        self.files = []

        if isinstance(content, (bytes, str)):
            if isinstance(content, bytes):
                zip_bytes = content
            else:
                zip_bytes = b64decode(content.encode())

            with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zip_file:
                for file_name in zip_file.namelist():
                    with zip_file.open(file_name) as fp:
                        self.files.append(File(name=file_name, content=fp.read()))
        elif isinstance(content, Iterable):
            self.files = list(content)
        elif isinstance(content, File):
            self.files = [content]
        elif isinstance(content, Filesystem):
            self.files = copy.deepcopy(content.files)
        elif content is None:
            self.files = []
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

    def __str__(self) -> str:
        """Create string representation of Filesystem object."""
        return b64encode(self.encode()).decode()

    def __iter__(self):
        return iter(self.files)
