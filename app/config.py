# app/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # This config now does two things:
    # 1. Tells Pydantic where to find the .env file.
    # 2. Makes the matching of variables case-sensitive.
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )

    # --- Field names MUST NOW EXACTLY MATCH the .env variable names ---

    # MongoDB Settings
    MONGODB_URI: str
    DATABASE_NAME: str

    # JWT Settings
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

# Create a single, reusable instance of the settings
settings = Settings()
# app/config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # --- Field names should be lowercase ---
    # pydantic-settings will automatically and case-insensitively
    # match these to your UPPERCASE environment variables.

    # MongoDB Settings
    mongodb_uri: str
    database_name: str

    # JWT Settings
    jwt_secret_key: str
    jwt_algorithm: str
    access_token_expire_minutes: int

    class Config:
        # This is the only configuration needed.
        # It tells Pydantic to load variables from the .env file.
        env_file = ".env"

# Create a single, reusable instance of the settings
settings = Settings()
