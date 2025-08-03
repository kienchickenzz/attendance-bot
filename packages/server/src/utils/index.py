from collections.abc import Generator
from typing import Annotated
from sqlmodel import Session
from fastapi import Depends

from redis import Redis

from database.engine import get_engine
from utils.redis_client import get_redis_client

from utils.redis_client import get_redis_client


def get_db() -> Generator[ Session, None, None ]:
    engine = get_engine()
    with Session( engine ) as session:
        yield session

SessionDep = Annotated[ Session, Depends( get_db ) ]

RedisDep = Annotated[ Redis, Depends( get_redis_client ) ]
