from app.services.storage import LocalStorage, S3Storage, get_storage


def test_get_storage_local(monkeypatch):
    monkeypatch.setattr("app.services.storage.settings.storage_backend", "local")
    storage = get_storage()
    assert isinstance(storage, LocalStorage)


def test_get_storage_s3(monkeypatch):
    monkeypatch.setattr("app.services.storage.settings.storage_backend", "s3")
    monkeypatch.setattr("app.services.storage.settings.s3_bucket", "test-bucket")
    monkeypatch.setattr("app.services.storage.settings.s3_region", "us-east-1")
    monkeypatch.setattr("app.services.storage.settings.s3_endpoint_url", "http://minio:9000")
    monkeypatch.setattr("app.services.storage.settings.s3_access_key", "minioadmin")
    monkeypatch.setattr("app.services.storage.settings.s3_secret_key", "minioadmin")
    monkeypatch.setattr("app.services.storage.settings.s3_create_bucket_if_missing", False)

    class DummyClient:
        def put_object(self, **kwargs):
            return kwargs

        def delete_object(self, **kwargs):
            return kwargs

    monkeypatch.setattr("app.services.storage.boto3.client", lambda *args, **kwargs: DummyClient())
    storage = get_storage()
    assert isinstance(storage, S3Storage)
