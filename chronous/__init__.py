# -*- coding: utf-8 -*-

"""
Asynchronous Event Based Architecture.

:copyright: (c) 2020 Lapis0875
:license: MIT, see LICENSE for more details.

"""

__title__ = "chronous"
__author__ = "Lapis0875"
__license__ = "MIT"
__copyright__ = "Copyright 2020 Lapis0875"
__version__ = "2.0.0"

__all__ = (
    "BaseArchitecture",
    "events"
)

from . import events
from .Architecture import BaseArchitecture
from .utils import getLogger, LogLevels

logger = getLogger("chronous", LogLevels.DEBUG)
