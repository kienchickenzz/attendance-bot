from pydantic import BaseModel, Field

class HealthCheckResponse( BaseModel ):
    status_code: int
    message: str

    timestamp: str

class DbHealthCheckResponse( BaseModel ):
    status_code: int
    message: str

    timestamp: str
    database_info: dict = Field(
        description="Chi tiết về trạng thái Weaviate database",
        examples=[ {
            "is_live": True,
            "is_ready": True,
            "version": "1.21.2",
        } ]
    )