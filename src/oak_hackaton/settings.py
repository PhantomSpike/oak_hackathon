from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    OAK_API_KEY: str
    OAK_API_URL: str
    OPENAI_API_KEY_OAK: str
    OPENAI_API_ORG_ID: str



def get_settings() -> Settings:
    return Settings()
