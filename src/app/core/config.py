from pathlib import Path

from pydantic import Field, BaseSettings, SecretStr


class Config(BaseSettings):
    secret_key: SecretStr = Field(..., env="SECRET_KEY")
    ip_address: str = Field(..., env="IP_ADDRESS")
    port: int = Field(..., env="PORT")

    jsw_algorithm: str = Field(..., env="JSW_ALGORITHM")
    access_token_expire_minutes: int = Field(..., env="ACCESS_TOKEN_EXPIRE_MINUTES")

    postgres_password: SecretStr = Field(..., env="POSTGRES_PASSWORD")
    backend_password: SecretStr = Field(..., env="BACKEND_PASSWORD")

    project_name = "Stress-Free Chat"
    version = "0.0.1"

    class Config:
        env_prefix = ""
        case_sensitive = True
        # Get the path to the directory of the current file
        current_dir = Path(__file__).resolve().parent
        # Traverse up the directory tree until the .env file is found
        while not (current_dir / ".env").exists():
            current_dir = current_dir.parent
        env_file = f"{current_dir}/.env"
        env_file_encoding = "utf-8"


config = Config()
