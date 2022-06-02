import sys

from loguru import logger

from logging import StreamHandler

logger.add(StreamHandler(sys.stderr), format='[{time}] [{level}] [{file.name}:{line}] gg {message}', level='INFO')
