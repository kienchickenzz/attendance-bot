from .feature.index import FeatureConfig
from .deploy.index import DeploymentConfig

from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict

from pathlib import Path

from dotenv import load_dotenv
from pathlib import Path


current_dir = Path( __file__ ).parent
env_file = current_dir / ".." / ".env"

# print( f"Loading .env from: { env_file }" )
# print( f"Load result: { load_dotenv( env_file ) }" )


class AppConfig(
    DeploymentConfig,
    FeatureConfig,
):
    model_config = SettingsConfigDict(
        env_file=env_file,
        env_file_encoding="utf-8",
        extra="ignore", # Ignore extra attributes
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[ BaseSettings ],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[ PydanticBaseSettingsSource, ... ]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )

app_config = AppConfig()
