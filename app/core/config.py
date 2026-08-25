from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_password: str
    database_user: str
    database_host: str
    database_port: int
    database_name: str

    secret_key: str
    algorithm: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
