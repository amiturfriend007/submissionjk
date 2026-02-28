from pydantic import AnyUrl, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # app
    title: str = "LuminaLib API"
    debug: bool = False

    # database
    database_url: AnyUrl = Field(..., env="DATABASE_URL")

    # jwt
    jwt_secret: str = Field(..., env="JWT_SECRET")
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60 * 24  # 1 day

    # storage
    storage_backend: str = "local"  # or "s3"
    storage_path: str = "./data"  # used by local backend
    s3_bucket: str = ""
    s3_region: str = ""
    s3_access_key: str = ""
    s3_secret_key: str = ""

    # llm
    llm_provider: str = "local"  # or "openai" etc
    llm_url: str = "http://localhost:8001"  # example for local llama API

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()