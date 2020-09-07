import datetime
import logging
from typing import Callable, Awaitable
from .Event import BaseEvent, EventContext, LISTENER


class Setup(BaseEvent):
    @staticmethod
    def listener(ec: EventContext):
        pass

    def __init__(self) -> None:
        super().__init__(name="setup")

    def add_listener(self, listener: LISTENER) -> None:
        super(Setup, self).add_listener(listener)


class Init(BaseEvent):

    @staticmethod
    def listener(ec: EventContext):
        pass

    def __init__(self):
        super().__init__(name="init")

    def add_listener(self, listener: Callable[[EventContext], Awaitable[None]]) -> None:
        super(Init, self).add_listener(listener)


class Start(BaseEvent):

    @staticmethod
    def listener(ec: EventContext, time: datetime.datetime):
        pass

    def __init__(self):
        super().__init__(name="start")

    def add_listener(self, listener: LISTENER) -> None:
        super(Start, self).add_listener(listener)


class Close(BaseEvent):

    @staticmethod
    def listener(ec: EventContext):
        pass

    def __init__(self):
        super().__init__(name="close")

    def add_listener(self, listener: LISTENER) -> None:
        super(Close, self).add_listener(listener)
