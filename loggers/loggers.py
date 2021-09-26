from pathlib import Path
import logging
import logging.handlers

DFLT_MAX_BYTES = 10 * 1024**2
DFLT_BACKUP_COUNT = 3
DFLT_MODE = "a"

def StdLogger(name, dirpath,
    mode = DFLT_MODE,
    maxBytes = DFLT_MAX_BYTES,
    backupCount = DFLT_BACKUP_COUNT,
    level = logging.DEBUG,
):
    "A factory function to set up a standard rotatig logger"

    dirpath = Path(dirpath).resolve()
    if dirpath.exists() and not dirpath.is_dir():
        raise Exception('{dirpath} is not a directory')

    dirpath.mkdir(parents=True, exist_ok=True)
    if not name: raise Exception('no logger name given')

    if not level: raise Exception('logger level missing')

    loggerFile = dirpath / (name + '.log')
    logger = logging.getLogger(name)

    handlers = [
        logging.StreamHandler(),
        logging.handlers.RotatingFileHandler(loggerFile,
            mode = mode, maxBytes = maxBytes, backupCount = backupCount,
        ),
    ]

    formatter = logging.Formatter(
        fmt = '%(asctime)s %(levelname)s: %(message)s',
        datefmt = '%Y-%m-%d %H:%M:%S',
    )

    for h in handlers:
        logger.addHandler(h)
        h.setFormatter(formatter)
    for obj in [logger] + handlers: obj.setLevel(level)

    return logger
