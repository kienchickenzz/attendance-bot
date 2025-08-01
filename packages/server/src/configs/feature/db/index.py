from pydantic_settings import BaseSettings
from pydantic import Field

from typing import Optional

class DBConfig( BaseSettings ):

    DB_TYPE: str = Field(
        description="",
    )

    DB_PORT: str = Field(
        description="",
    )

    DB_HOST: str = Field(
        description="",
    )

    DB_DATABASE: str = Field(
        description="",
    )

    DB_USERNAME: str = Field(
        description="",
    )

    DB_PASSWORD: str = Field(
        description="",
    )


    # ----------
    # Advanced Config
    # ----------


    SQLALCHEMY_POOL_SIZE: int = Field(
        description="",
    )

    SQLALCHEMY_POOL_RECYCLE: int = Field(
        description="",
    )

    SQLALCHEMY_ECHO: bool = Field(
        description="",
    )

    POSTGRES_MAX_CONNECTIONS: int = Field(
        description="",
    )

    POSTGRES_SHARED_BUFFERS: str = Field(
        description="",
    )

    POSTGRES_WORK_MEM: str = Field(
        description="",
    )

    POSTGRES_MAINTENANCE_WORK_MEM: str = Field(
        description="",
    )

    POSTGRES_EFFECTIVE_CACHE_SIZE: str = Field(
        description="",
    )
