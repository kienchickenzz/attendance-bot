from pydantic import Field
from pydantic_settings import BaseSettings


class DeploymentConfig( BaseSettings ):
    """
    Configuration settings for application deployment
    """

    APPLICATION_NAME: str = Field(
        description="Name of the application, used for identification and logging purposes",
        default="",
    )

    DEBUG: bool = Field(
        description="Enable debug mode for additional logging and development features",
        default=True,
    )

    # Request logging configuration
    ENABLE_REQUEST_LOGGING: bool = Field(
        description="Enable request and response body logging",
        default=True,
    )
