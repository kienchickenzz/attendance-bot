from pydantic_settings import BaseSettings
from pydantic import Field

from typing import Optional

class MainConfig( BaseSettings ):
    """
    Configuration for application
    """

    OLLAMA_URL: Optional[ str ] = Field(
        description="",
        default=None,
    )

    OLLAMA_EMBEDDING_MODEL: Optional[ str ] = Field(
        description="",
        default=None,
    )

    GEMINI_API_KEY: Optional[ str ] = Field(
        description="",
        default=None,
    )

    GEMINI_MODEL: Optional[ str ] = Field(
        description="",
        default=None,
    )

    WEAVIATE_URL: Optional[ str ] = Field(
        description="Format string for log messages",
        default=None,
    )
