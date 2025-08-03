from fastapi import FastAPI

from utils import redis_client

async def init_app( app: FastAPI ):
    await redis_client.init()
