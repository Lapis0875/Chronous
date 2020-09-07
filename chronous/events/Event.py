from __future__ import annotations

import asyncio
import inspect
import logging
from typing import Dict, List, Awaitable, Any, Type, Callable, Optional, NoReturn

logger = logging.getLogger("chronous")


class EventMeta(type):
    event_tracks: Dict[str, object] = {}

    def __new__(metacls, clsname, bases, namespace, **kwargs):
        cls = super(EventMeta, metacls).__new__(metacls, clsname, bases, namespace)
        metacls.event_tracks.update({cls.__name__: cls})
        logger.debug(metacls.event_tracks)
        return cls

    def get_tracking_events(cls) -> Dict[str, object]:
        return cls.event_tracks


class EventContext:
    def __init__(self, event: Type[BaseEvent]) -> None:
        self.event = event

    def __repr__(self) -> str:
        return "<EventContext:event={0}>".format(self.event.name)


class EventException(Exception):
    def __init__(self, event: BaseEvent, msg: Optional[str] = None) -> None:
        self.event = event
        self.msg = (msg if msg is not None
                    else "Unexpected exception has been occured during processing event: {0}".format(event.name))

    def __repr__(self) -> str:
        return "<EventException:event={0}>".format(self.event.name)


class MalformedListenerException(EventException):
    def __init__(self, event: BaseEvent, malformed_listener: LISTENER, expected_listener_format: inspect.Arguments) -> None:
        self.malformed_listener: LISTENER = malformed_listener
        self.expected_listener_format: inspect.Arguments = expected_listener_format
        self.malformed_format: inspect.Arguments = inspect.getargs(self.malformed_listener.__code__)
        msg = ("Listener is malformed! : listener args {0} does not match with expected listener format {1}"
               .format(self.malformed_format, self.expected_listener_format))
        super(MalformedListenerException, self).__init__(event, msg)

    def __repr__(self) -> str:
        return ("<MalformedListenerException:event={0},malformed_listener:{1},malformed_format:{2}>"
                .format(self.event.name, self.malformed_listener, self.malformed_format))


class ListenerException(EventException):
    def __init__(self, event: BaseEvent, listener: LISTENER, original: Type[BaseException]):
        msg: str = "Listener {0!r} raised exception {1.__class__.__name__} : {1}".format(listener, original)
        super(ListenerException, self).__init__(event, msg)
        self.listener: LISTENER = listener
        self.original: Type[BaseException] = original

    def __repr__(self) -> str:
        return ("<ListenerException:event={0},listener={1},original={2}>"
                .format(self.event.name, self.listener, self.original))


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

    def register_listener(self, listener: LISTENER) -> NoReturn:
        """
        Add listener in event`s listener list.
        :param listener: listener to add
        """
        if not asyncio.iscoroutinefunction(listener):
            logger.error(
                msg="Given listener {0} is not coroutine function! It must be defined using 'async def'"
                    .format(listener)
            )
            raise TypeError("Listeners must be coroutine function (defined using 'async def')")

        # inspect arguments in :param listener: and event`s listener template (staticmethod 'listener')
        if inspect.getargs(listener.__code__) != inspect.getargs(self.listener.__code__):
            # :param listener: does not have same arguments with event`s listener template. Malformed!
            raise MalformedListenerException(
                event=self,
                malformed_listener=listener,
                expected_listener_format=inspect.getargs(self.listener.__code__)
            )
        self.listeners.append(listener)

    # alias
    add_listener: Callable[[object, LISTENER], NoReturn] = register_listener

    # TODO : Add some ways to remove listener. Maybe restricting @listen decorator to get unique name for listener?

    async def dispatch(self, *args, **kwargs) -> NoReturn:
        """
        Dispatch the event.
        Call all registered listeners with given parameters.
        :param args: positional arguments used in listener
        :param kwargs: keyword arguments used in listener
        """
        logger.debug("listeners : {0}".format(self.listeners))
        tasks: List[asyncio.Task] = []
        for i, listener in enumerate(self.listeners):
            logger.debug("Wrapping listener_{0} {1} into asyncio.Task instance.".format(i, listener))
            listener_task = asyncio.create_task(
                listener(
                    EventContext(event=self),
                    *args,
                    **kwargs
                ),
                name="dispatch_{0}_{1}".format(self.name, i)
            )
            tasks.append(listener_task)
        logger.debug("Await all tasks")
        results = await asyncio.gather(*tasks)
        logger.debug("Dispatch results : {0}".format(results))
        for i, result in enumerate(results):
            logger.debug("Dispatch {0} result : {1}".format(i, result))
            if isinstance(result, Exception):
                logger.debug("Found Exception on the result of dispatch {0}. Raising ListenerException...".format(i))
                raise ListenerException(event=self, listener=self.listeners[i], original=result)


# Type hints
EVENT = Type[BaseEvent]
LISTENER = Callable[..., Awaitable[None]]