from typing import Optional, List

from pydantic import BaseModel

from models.search import TimePeriod

class SessionContext( BaseModel ):
    # start_date: Optional[ str ] = None
    # end_date: Optional[ str ] = None
    time_query: Optional[ List[ TimePeriod ] ] = None
    topic: Optional[ str ] = None
    prev_question: Optional[ str ] = None

class UpsertSessionRequest( BaseModel ):
    session_id: Optional[ str ] = None
    data: Optional[ SessionContext ] = None

class GetSessionResponse( BaseModel ):
    session_id: str
    data: Optional[ SessionContext ] = None
    expires_in: int
