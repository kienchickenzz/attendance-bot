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
