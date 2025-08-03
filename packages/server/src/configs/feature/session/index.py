from pydantic_settings import BaseSettings
from pydantic import Field

from typing import Optional

class SessionConfig( BaseSettings ):

    REDIS_HOST: str = Field(
        description="",
    )

    REDIS_PORT: str = Field(
        description="",
    )
    
    REDIS_PASSWORD: str = Field(
        description="",
    )

    REDIS_DB: str = Field(
        description="",
    )

    REDIS_TTL: int = Field(
        description="",
    )
