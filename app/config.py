# app/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    This class defines and loads all configuration settings for the application.
    It automatically reads from environment variables and/or a .env file.
    
    Pydantic-settings is case-insensitive, so the lowercase fields below will
    correctly map to the uppercase variables in your .env file.
    """
    
    # MongoDB Settings
    mongodb_uri: str
    database_name: str

    # JWT Authentication Settings
    jwt_secret_key: str
    jwt_algorithm: str
    access_token_expire_minutes: int

    # This model_config dictionary tells Pydantic how to behave.
    model_config = SettingsConfigDict(
        # Specifies the name of the file to load environment variables from.
        # This file should be in the root directory of your project.
        env_file='.env',
        
        # This is a crucial setting for compatibility and robustness.
        # It tells Pydantic to ignore any extra environment variables
        # it finds that are not explicitly defined in this class.
        extra='ignore'
    )

# This creates a single, global instance of your settings.
# All other parts of your application should import this 'settings' object.
settings = Settings()
