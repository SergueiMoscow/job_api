import logging
import colorlog


class Logger:
    logger = None
    formatter = None
    level = logging.DEBUG
    stream_handler = None

    @classmethod
    def __init__(cls):
        if cls.stream_handler is None:
            cls.init()

    @classmethod
    def init(cls):
        if cls.stream_handler is None:
            cls.logger = logging.getLogger(__name__)
            cls.formatter = colorlog.ColoredFormatter(
                '%(log_color)s%(levelname)s:%(name)s:%(message)s',
                log_colors={
                    'DEBUG': 'cyan',
                    'INFO': 'green',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'red,bg_white',
                }
            )
            cls.logger.setLevel(cls.level)

            cls.stream_handler = logging.StreamHandler()
            cls.stream_handler.setLevel(cls.level)
            cls.stream_handler.setFormatter(cls.formatter)

            cls.logger.addHandler(cls.stream_handler)

    @classmethod
    def debug(cls, msg):
        cls.init()
        cls.logger.debug(msg)

    @classmethod
    def info(cls, msg):
        cls.init()
        cls.logger.info(msg)

    @classmethod
    def warning(cls, msg):
        cls.init()
        cls.logger.warning(msg)

    @classmethod
    def error(cls, msg):
        cls.init()
        cls.logger.error(msg)

    @classmethod
    def critical(cls, msg):
        cls.init()
        cls.logger.critical(msg)


def debug(msg):
    Logger.debug(msg)


def info(msg):
    Logger.info(msg)


def warning(msg):
    Logger.warning(msg)


def error(msg):
    Logger.error(msg)


def critical(msg):
    Logger.critical(msg)


if __name__ == '__main__':
    debug('testing debug')
    info('testing info')
    warning('testing warning')
    error('testing error')
    critical('testing critical')


