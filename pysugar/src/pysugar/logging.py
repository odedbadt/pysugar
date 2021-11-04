import logging
import sys
FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

def configure_logger(
    name='root',
    level=logging.INFO,
    stdout=True,
    outputfile=None):
    logging.getLogger().setLevel(level)
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if outputfile:
        handler = logging.FileHandler(outputfile)
    elif stdout:
        handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    formatter = logging.Formatter(FORMAT)
    handler.setFormatter(formatter)
    logger.handlers = []
    logger.addHandler(handler)
    return logger
