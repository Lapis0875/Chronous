# -*- coding: utf-8 -*-

"""
Asynchronous Event Based Architecture.

Copyright:
    (c) 2020 Lapis0875
License:
    MIT, see LICENSE for more details.
"""

__title__ = "chronous"
__author__ = "Lapis0875"
__license__ = "MIT"
__copyright__ = "Copyright 2020 Lapis0875"
__version__ = "2.0.0b4"

__all__ = (
    "events"
)

from . import events
from .utils import getLogger, LogLevels

logger = getLogger("chronous", LogLevels.DEBUG)
