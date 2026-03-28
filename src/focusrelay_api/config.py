from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    focusrelay_bin: str = "focusrelay"
    command_timeout: float = 30.0
    host: str = "0.0.0.0"
    port: int = 8394
    api_token: str = ""

    model_config = {"env_prefix": "FOCUSRELAY_"}


settings = Settings()
