from fastapi import FastAPI

from database import engine

def init_app( app: FastAPI ):
    engine.init()
