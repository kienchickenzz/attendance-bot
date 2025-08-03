from .logging.index import LoggingConfig
from .main.index import MainConfig
from .db.index import DBConfig
from .session.index import SessionConfig

class FeatureConfig(
    # Place configs in alphabet order
    DBConfig,
    LoggingConfig,
    MainConfig,
    SessionConfig,
):
    pass
