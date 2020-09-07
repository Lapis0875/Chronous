import asyncio
import logging
from typing import Dict, NoReturn, Optional
from .events import EVENT, LISTENER, BaseEvent, MalformedListenerException

logger = logging.getLogger("chronous")


class BaseArchitecture:

    def __init__(self, name: str):
        self.__name = name
        self.__event_loop = asyncio.get_event_loop()
        self.__events: Dict[str, EVENT] = {}

    def registerEvent(self, event: EVENT):
        if not isinstance(event, (BaseEvent, )):
            raise TypeError("Event must inherit the class 'BaseEvent' to be registered")
        if event.name not in self.__events.keys():
            logger.debug(f"Registering event : {event}")
            self.__events.update({event.name.lower(): event})
        logger.debug(self.__events)

    def registerListener(self, listener: LISTENER, event_name: Optional[str] = None) -> None:
        """
        Register listener in event.
        :param observer_coro: observer function
        :param event_name:
        :param args:
        :param kwargs:
        :return: None
        :raise TypeError: if listener is not a coroutine function
        """
        event_name = listener.__name__ if event_name is None else event_name

        if event_name in self.__events.keys():
            event: EVENT = self.__events.get(event_name)
            try:
                event.add_listener(listener=listener)
            except MalformedListenerException as e:
                logger.debug("Given listener does not match with exepected format. Rejetcing...")

        else:
            logger.error("Given listener indicates unknown event {event}."
                         "Cannot register listener!".format(event=event_name))
            raise KeyError("Unknown event to register")

    def listen(self, event_name: Optional[str] = None):
        logger.debug("decorator 'listen' called with event name : {event_name}".format(event_name=event_name))

        def decorator(listener_coro: LISTENER):
            logger.debug("Checking function inside @listen : {listener}".format(listener=listener_coro))
            self.registerListener(listener=listener_coro, event_name=event_name)
            return listener_coro
        return decorator

    async def dispatch(self, event_name: str, *args, **kwargs) -> NoReturn:
        logger.debug("Try dispatching event...")
        event_name = event_name.lower()
        if event_name in self.__events.keys():
            logger.debug("Found event {event_name}! dispatching..".format(event_name=event_name))
            await self.__events.get(event_name).dispatch(*args, **kwargs)

    def run(self) -> NoReturn:
        asyncio.run(self.process())

    async def process(self) -> NoReturn:
        raise NotImplementedError("Architectures must subclass the class 'BaseArchitecture'"
                                  "and override the coroutine method 'process'")
