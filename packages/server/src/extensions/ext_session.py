from fastapi import FastAPI

from utils import redis_client

def init_app( app: FastAPI ):
    redis_client.init()
