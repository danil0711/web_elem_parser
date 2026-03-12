from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    
    # Database
    postgres_user: str
    postgres_password: str
    postgres_db: str

    postgres_host: str = "localhost"
    postgres_port: int = 5436

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379

 
    # JWT
    secret_key: str
    algorithm: str = 'HS256'
    access_token_expire_minutes: int = 1
    refresh_token_expire_days: int = 60 * 24 * 7
    
    
    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.postgres_user}:"
            f"{self.postgres_password}@"
            f"{self.postgres_host}:"
            f"{self.postgres_port}/"
            f"{self.postgres_db}"
        )


settings = Settings()