from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    admin: SecretStr
    telegram_id: SecretStr
    telegram_hash: SecretStr
    telegram_bot_api: SecretStr
    bybit_api: SecretStr
    bybit_secret: SecretStr

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


info = Settings()
