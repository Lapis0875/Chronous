from __future__ import annotations

import asyncio
from typing import Dict, List, Awaitable, Tuple, Any, Type, Callable, Optional


class EventMeta(type):
    event_tracks: Dict[str, object] = {}

    def __new__(metacls, clsname, bases, namespace, **kwargs):
        cls = super(EventMeta, metacls).__new__(metacls, clsname, bases, namespace)
        metacls.event_tracks.update({cls.__name__: cls})
        print(metacls.event_tracks)
        return cls


class EventContext:
    def __init__(self, event: Type[BaseEvent], *args: Optional[Any], **kwargs: Optional[Any]) -> None:
        self.event = event
        self.args = args
        self.kwargs = kwargs


class BaseEvent(metaclass=EventMeta):
    __name: str = ""

    def __init__(self, name=None):
        self.__name = name if name is not None else self.__name__
        self.listeners: List[Callable[[EventContext], Awaitable[None]]] = []

    @property
    def name(self) -> str:
        return self.__name

    @staticmethod
    def listener(event: Type[BaseEvent]):
        # Please override this listener method in your needs
        raise NotImplementedError("Listener template not implemented!")

    def add_listener(self, listener: Callable[[EventContext], Awaitable[None]]) -> None:
        if not asyncio.iscoroutinefunction(listener):
            raise TypeError("Listeners must be coroutines (defined using 'async def')")
        print(listener)
        # print(listener.__func__.__args__)
        # print(listener.__func__.__kwargs__)
        # print(listener.__func__.__annotations__)
        self.listeners.append(listener)

    async def dispatch(self):
        print(f"listeners : {self.listeners}")
        for listener in self.listeners:
            await listener(
                EventContext(
                    event=self
                )
            )


# Type hints
EVENT = Type[BaseEvent]
LISTENER = Callable[[Type[BaseEvent]], Awaitable[None]]