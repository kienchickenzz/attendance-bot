from database import engine

def init_app( app ):
    return engine.init()
