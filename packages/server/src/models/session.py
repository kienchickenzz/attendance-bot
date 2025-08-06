from typing import Optional

from pydantic import BaseModel

class SessionContext( BaseModel ):
    start_date: Optional[ str ] = None
    end_date: Optional[ str ] = None
    topic: Optional[ str ] = None
    prev_question: Optional[ str ] = None

class UpsertSessionRequest( BaseModel ):
    session_id: Optional[ str ] = None
    data: Optional[ SessionContext ] = None

class GetSessionResponse( BaseModel ):
    session_id: str
    data: Optional[ SessionContext ] = None
    expires_in: int
