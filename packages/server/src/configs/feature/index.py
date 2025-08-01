from .logging.index import LoggingConfig
from .main.index import MainConfig
from .db.index import DBConfig

class FeatureConfig(
    # Place configs in alphabet order
    DBConfig,
    LoggingConfig,
    MainConfig
):
    pass
