# -*- coding: utf-8 -*-

"""
Asynchronous Game Library
~~~~~~~~~~~~~~~~~~~

AsyncIO based game library.
Implements only Event-based game architecture using asyncio, and other stuffs like gui are not.

:copyright: (c) 2020 Lapis0875
:license: MIT, see LICENSE for more details.

"""

__title__ = "chronous"
__author__ = "Lapis0875"
__license__ = "MIT"
__copyright__ = "Copyright 2020 Lapis0875"
__version__ = "1.0.0"

from .Architecture import *
from . import events

import sys, logging
from colorlog import ColoredFormatter

logger = logging.getLogger("chronous")
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(
    ColoredFormatter(
        "{log_color}[{asctime}] [{levelname}] {name}: {message}",
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white,bold',
        },
        secondary_log_colors={},
        style='{'
    )
)
logger.addHandler(console_handler)