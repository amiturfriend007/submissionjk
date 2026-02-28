from abc import ABC, abstractmethod
from pathlib import Path
from typing import BinaryIO

from app.core.config import settings


class StorageBackend(ABC):
    @abstractmethod
    async def save(self, fileobj: BinaryIO, filename: str) -> str:
        """Save the file object and return a path or key."""

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Remove the file identified by key."""


class LocalStorage(StorageBackend):
    def __init__(self, base_path: str | Path | None = None):
        self.base = Path(base_path or settings.storage_path)
        self.base.mkdir(parents=True, exist_ok=True)

    async def save(self, fileobj: BinaryIO, filename: str) -> str:
        dest = self.base / filename
        # write in async way maybe but simple blocking is okay for prototype
        with open(dest, "wb") as f:
            f.write(fileobj.read())
        return str(dest)

    async def delete(self, key: str) -> None:
        p = Path(key)
        if p.exists():
            p.unlink()


# additional implementations (S3) would follow same interface


def get_storage() -> StorageBackend:
    if settings.storage_backend == "local":
        return LocalStorage()
    # elif settings.storage_backend == "s3":
    #     return S3Storage(...)  # not implemented
    raise NotImplementedError(f"Unknown storage backend {settings.storage_backend}")