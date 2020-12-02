import asyncio
import logging
from typing import NoReturn
from .events import BaseEvent, EventBus

logger = logging.getLogger("chronous")


class BaseArchitecture:

    def __init__(self, name: str, bus: EventBus):
        self._name = name
        self._bus: EventBus = bus
        self._eventLoop = bus.eventLoop

    @property
    def bus(self) -> EventBus:
        return self._bus

    @property
    def eventLoop(self) -> asyncio.AbstractEventLoop:
        return self._eventLoop

    def registerEvent(self, event: BaseEvent):
        self._bus.registerEvent(event)
        logger.debug('currently registered events : {events}'.format(events=self._bus.events))

    def run(self) -> NoReturn:
        self._eventLoop.run_until_complete(self.process())

    async def process(self) -> NoReturn:
        raise NotImplementedError("Architectures must subclass the class 'BaseArchitecture'"
                                  "and override the coroutine method 'process'")
