import asyncio
from functools import wraps
from typing import Dict, Type, Coroutine, NoReturn, Callable, Any, Awaitable, Optional
from .events import BaseEvent, EVENT, LISTENER, Setup, Init, Close, EventContext


class BaseArchitecture:
    __name: str = ""
    __event_loop: asyncio.AbstractEventLoop = None
    __events: Dict[str, EVENT] = {}

    def __init__(self, game_name: str):
        self.__name = game_name
        self.__event_loop = asyncio.get_event_loop()

    def registerEvent(self, event: EVENT):
        if event.name not in self.__events.keys():
            print(f"Registering event : {event}")
            self.__events.update({event.name.lower(): event})
        print(self.__events)

    def registerListener(self, listener: LISTENER, event_name: Optional[str] = None) -> None:
        """

        :param observer_coro: observer function
        :param event_name:
        :param args:
        :param kwargs:
        :return: None
        :raise TypeError: if listener is not a coroutine function
        """
        if not asyncio.iscoroutine(listener):
            raise TypeError("event listener must be a coroutine")

        event_name = listener.__name__ if event_name is None else event_name

        if event_name in [event_name for event_name in self.__events.keys()]:
            event: EVENT = self.__events.get(event_name)
            event.add_listener(listener=listener)
        else:
            raise KeyError("Unknown event to register")

    def listen(self, event_name: Optional[str] = None):
        print("decorator 'listener' called!")

        @wraps
        def decorator(listener_coro: LISTENER):
            print(listener_coro)
            self.registerListener(listener=listener_coro, event_name=event_name)
            return listener_coro

        print("created decorator function. returning...")

        return decorator

    async def dispatch(self, event_name: str) -> NoReturn:
        print("Try dispatching event...")
        event_name = event_name.lower()
        if event_name in self.__events.keys():
            print(f"Found event {event_name}! dispatching..")
            await self.__events.get(event_name).dispatch()

    def run(self) -> NoReturn:
        asyncio.run(self.process())

    async def process(self) -> NoReturn:
        raise NotImplementedError("Architectures must subclass the class 'BaseArchitecture'"
                                  "and override the coroutine method 'process'")
