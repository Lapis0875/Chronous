from __future__ import annotations

import asyncio
import inspect
import logging
from typing import Dict, List, Awaitable, Any, Type, Callable, Optional

logger = logging.getLogger("chronous")


class EventMeta(type):
    event_tracks: Dict[str, object] = {}

    def __new__(metacls, clsname, bases, namespace, **kwargs):
        cls = super(EventMeta, metacls).__new__(metacls, clsname, bases, namespace)
        metacls.event_tracks.update({cls.__name__: cls})
        logger.debug(metacls.event_tracks)
        return cls


class EventContext:
    def __init__(self, event: Type[BaseEvent], *args: Optional[Any], **kwargs: Optional[Any]) -> None:
        self.event = event
        self.args = args
        self.kwargs = kwargs


class EventException(Exception):
    def __init__(self, event: BaseEvent, msg: Optional[str] = None) -> None:
        self.event = event
        self.msg = msg if msg is not None else f"Unexpected exception has been occured during processing event: {event.name}"

    def __repr__(self) -> str:
        return f"<EventException:event={self.event.name}>"


class MalformedListenerException(EventException):
    def __init__(self, event: BaseEvent, malformed_listener: LISTENER, expected_listener_format: inspect.Arguments) -> None:
        msg = f"Listener is malformed! : {malformed_listener} does not match with expected listener format." \
              f""
        logger.debug(MalformedListenerException, self).__init__(event=event, msg=msg)
        self.malformed_listener: LISTENER = malformed_listener
        self.expected_listener_format: inspect.Arguments = expected_listener_format

    def __repr__(self) -> str:
        return f"<MalformedListenerException:event={self.event.name}," \
               f"malformed_listener:{self.malformed_listener}" \
               f"malformed_format:{inspect.getargs(self.malformed_listener.__code__)}>" \
               f"expected_format:{self.expected_listener_format}>"


class ListenerException(EventException):
    def __init__(self, event: BaseEvent, listener: LISTENER, original: Type[BaseException]):
        msg: str = "Listener {0!r} raised exception {1.__class__.__name__} : {1}".format(listener, original)
        super(ListenerException, self).__init__(event=event)
        self.listener: LISTENER = listener
        self.original: Type[BaseException] = original

    def __repr__(self) -> str:
        return f"<ListenerException:event={self.event.name},listener={self.listener},original={self.original}>"


class BaseEvent(metaclass=EventMeta):
    __name: str = ""

    def __init__(self, name=None):
        self.__name = name if name is not None else self.__name__
        self.listeners: List[LISTENER] = []

    @property
    def name(self) -> str:
        return self.__name

    @staticmethod
    def listener(ec: EventContext, *args, **kwargs):
        # Please override this listener method in your needs
        raise NotImplementedError("Listener template not implemented!")

    def add_listener(self, listener: LISTENER) -> None:
        if not asyncio.iscoroutinefunction(listener):
            logger.error(f"Given listener {listener} is not coroutine function! It must be defined using 'async def'")
            raise TypeError("Listeners must be coroutine function (defined using 'async def')")
        if inspect.getargs(listener.__code__) != inspect.getargs(self.listener.__code__):
            raise MalformedListenerException(
                event=self,
                malformed_listener=listener,
                expected_listener_format=inspect.getargs(self.listener.__code__)
            )
        self.listeners.append(listener)

    def inspect_listener(self, listener: LISTENER) -> None:
        """
        @Replection
        Debug method to inspect given listener and compare with Class`s listener format.
        :param listener: Given listener instance
        """
        inspect_given: inspect.Arguments = inspect.getargs(listener.__code__)
        inspect_format: inspect.Arguments = inspect.getargs(self.listener.__code__)
        logger.debug('='*20)
        logger.debug(f"[{self.name}.add_listener] given_listener -> instance : {listener}")
        logger.debug(f"[{self.name}.add_listener] given_listener -> __doc__ : {listener.__doc__}")
        logger.debug(f"[{self.name}.add_listener] given_listener -> __dict__ : {listener.__dict__}")
        logger.debug(f"[{self.name}.add_listener] given_listener -> __annotations__ : {listener.__annotations__}")
        logger.debug(f"[{self.name}.add_listener] given_listener -> __defaults__ : {listener.__defaults__}")
        logger.debug(f"[{self.name}.add_listener] given_listener -> __kwdefaults__ : {listener.__kwdefaults__}")
        logger.debug(f"[{self.name}.add_listener] given_listener -> __code__ : {listener.__code__}")
        logger.debug(f"[{self.name}.add_listener] given_listener -> inspect args : {inspect_given}")
        logger.debug(f"[{self.name}.add_listener] given_listener -> type() : {type(listener)}")
        logger.debug(f"[{self.name}.add_listener] given_listener -> dir() : {dir(listener)}")
        logger.debug('='*20)
        logger.debug(f"[{self.name}.add_listener] given_listener -> instance : {self.listener}")
        logger.debug(f"[{self.name}.add_listener] listener_format -> __doc__ : {self.listener.__doc__}")
        logger.debug(f"[{self.name}.add_listener] listener_format -> __dict__ : {self.listener.__dict__}")
        logger.debug(f"[{self.name}.add_listener] listener_format -> __annotations__ : {self.listener.__annotations__}")
        logger.debug(f"[{self.name}.add_listener] listener_format -> __defaults__ : {self.listener.__defaults__}")
        logger.debug(f"[{self.name}.add_listener] listener_format -> __kwdefaults__ : {self.listener.__kwdefaults__}")
        logger.debug(f"[{self.name}.add_listener] listener_format -> __code__ : {self.listener.__code__}")
        logger.debug(f"[{self.name}.add_listener] listener_format -> inspect args : {inspect_format}")
        logger.debug(f"[{self.name}.add_listener] listener_format -> type() : {type(self.listener)}")
        logger.debug(f"[{self.name}.add_listener] listener_format -> dir() : {dir(self.listener)}")
        logger.debug('='*20)

    async def dispatch(self, *args, **kwargs):
        logger.debug(f"listeners : {self.listeners}")
        current_listener: LISTENER = None
        try:
            for listener in self.listeners:
                current_listener = listener
                await listener(
                    EventContext(
                        event=self
                    ),
                    *args, **kwargs
                )
        except Exception as e:
            raise ListenerException(event=self, listener=current_listener, original=e)


# Type hints
EVENT = Type[BaseEvent]
LISTENER = Callable[..., Awaitable[None]]