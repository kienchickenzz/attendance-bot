import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from configs.index import app_config


def init_app( app ):
    log_handlers: list[ logging.Handler ] = []
    log_file = app_config.LOG_FILE
    log_file = ""
    if log_file:
        log_dir = os.path.dirname( log_file )
        os.makedirs( log_dir, exist_ok=True )
        log_handlers.append(
            RotatingFileHandler(
                filename=log_file,
                maxBytes=app_config.LOG_FILE_MAX_SIZE * 1024 * 1024,
                backupCount=app_config.LOG_FILE_BACKUP_COUNT,
            )
        )

    # Always add StreamHandler to log to console
    sh = logging.StreamHandler( sys.stdout )
    log_handlers.append( sh )

    logging.basicConfig(
        level=app_config.LOG_LEVEL,
        format=app_config.LOG_FORMAT,
        datefmt=app_config.LOG_DATEFORMAT,
        handlers=log_handlers,
        force=True,
    )
