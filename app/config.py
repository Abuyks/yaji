from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    secret_key: str
    mail_username: str
    mail_password: str
    mail_from: str
    database_url: str
    s3_bucket_name: str
    algorithm: str
    email_token_expire_minutes: int
    access_token_expire_minutes: int

    class Config:
        env_file = ".env"


settings = Settings()