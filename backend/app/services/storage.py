from abc import ABC, abstractmethod
from pathlib import Path
from typing import BinaryIO
from uuid import uuid4

import boto3
from botocore.exceptions import ClientError

from app.core.config import settings


class StorageBackend(ABC):
    @abstractmethod
    async def save(self, fileobj: BinaryIO, filename: str) -> str:
        """Save the file object and return a path or key."""

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Remove the file identified by key."""

    @abstractmethod
    async def get_download_url(
        self,
        key: str,
        expires_seconds: int = 3600,
        disposition: str = "attachment",
        content_type: str | None = None,
    ) -> str | None:
        """Return a temporary URL when storage supports it (e.g. S3)."""


class LocalStorage(StorageBackend):
    def __init__(self, base_path: str | Path | None = None):
        self.base = Path(base_path or settings.storage_path)
        self.base.mkdir(parents=True, exist_ok=True)

    async def save(self, fileobj: BinaryIO, filename: str) -> str:
        safe_name = Path(filename).name
        dest = self.base / f"{uuid4().hex}_{safe_name}"
        # write in async way maybe but simple blocking is okay for prototype
        with open(dest, "wb") as f:
            f.write(fileobj.read())
        return str(dest)

    async def delete(self, key: str) -> None:
        p = Path(key)
        if p.exists():
            p.unlink()

    async def get_download_url(
        self,
        key: str,
        expires_seconds: int = 3600,
        disposition: str = "attachment",
        content_type: str | None = None,
    ) -> str | None:
        return None


class S3Storage(StorageBackend):
    def __init__(
        self,
        bucket: str | None = None,
        region: str | None = None,
        endpoint_url: str | None = None,
    ):
        self.bucket = bucket or settings.s3_bucket
        if not self.bucket:
            raise ValueError("s3_bucket must be configured when STORAGE_BACKEND=s3")

        self.prefix = settings.s3_object_prefix.strip("/") if settings.s3_object_prefix else ""
        self.client = boto3.client(
            "s3",
            region_name=region or settings.s3_region or None,
            endpoint_url=endpoint_url or settings.s3_endpoint_url or None,
            aws_access_key_id=settings.s3_access_key or None,
            aws_secret_access_key=settings.s3_secret_key or None,
        )

        if settings.s3_create_bucket_if_missing:
            self._ensure_bucket()

    def _ensure_bucket(self) -> None:
        try:
            self.client.head_bucket(Bucket=self.bucket)
        except ClientError:
            # Works for AWS S3 and local S3-compatible providers like MinIO.
            self.client.create_bucket(Bucket=self.bucket)

    def _build_key(self, filename: str) -> str:
        safe_name = Path(filename).name
        name = f"{uuid4().hex}_{safe_name}"
        return f"{self.prefix}/{name}" if self.prefix else name

    async def save(self, fileobj: BinaryIO, filename: str) -> str:
        key = self._build_key(filename)
        self.client.put_object(Bucket=self.bucket, Key=key, Body=fileobj.read())
        return key

    async def delete(self, key: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=key)

    async def get_download_url(
        self,
        key: str,
        expires_seconds: int = 3600,
        disposition: str = "attachment",
        content_type: str | None = None,
    ) -> str | None:
        filename = Path(key).name.split("_", 1)[1] if "_" in Path(key).name else Path(key).name
        params = {
            "Bucket": self.bucket,
            "Key": key,
            "ResponseContentDisposition": f'{disposition}; filename="{filename}"',
        }
        if content_type:
            params["ResponseContentType"] = content_type

        return self.client.generate_presigned_url(
            ClientMethod="get_object",
            Params=params,
            ExpiresIn=expires_seconds,
        )


def get_storage() -> StorageBackend:
    if settings.storage_backend == "local":
        return LocalStorage()
    if settings.storage_backend == "s3":
        return S3Storage()
    raise NotImplementedError(f"Unknown storage backend {settings.storage_backend}")
