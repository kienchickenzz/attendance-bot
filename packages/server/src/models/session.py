from typing import Optional

from pydantic import BaseModel

class SessionContext( BaseModel ):
    topic: Optional[ str ]
    start_date: Optional[ str ] = None
    end_date: Optional[ str ] = None

class CreateSessionRequest( BaseModel ):
    session_id: str
    data: Optional[ SessionContext ] = None

class GetSessionResponse( BaseModel ):
    session_id: str
    data: Optional[ SessionContext ] = None
    expires_in: int
