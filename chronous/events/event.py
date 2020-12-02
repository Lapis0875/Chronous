from __future__ import annotations

import asyncio
import inspect
from warnings import warn
import traceback
from abc import abstractmethod
from typing import Dict, List, Optional, NoReturn, Any, Tuple
from chronous.utils import CLASS, CoroutineFunction, getLogger, LogLevels, Logger

__all__ = (
    "EventStorage",
    "EventMeta",
    "BaseEvent",
    "EventException",
    "ListenerDispatchException"
)

logger: Logger = getLogger("chronous.events.event", LogLevels.DEBUG)


class EventStorage:
    """
    Storage object containing and tracking all event classes and instances.
    """
    __classes: Dict[str, CLASS] = {}  # Event class tracker
    __instances: Dict[CLASS, EventMeta] = {}  # Event instance tracker

    @classmethod
    def registerEventClass(cls, eventClass: CLASS):
        """Register event class.
        Used in metaclass 'EventMeta' to register created event class.

        Args:
            eventClass: new event class object.
        """
        try:
            registered = cls.__classes[eventClass.__name__]
            raise ValueError("Event named {!r} already registered!".format(registered))
        except KeyError:
            cls.__classes[eventClass.__name__] = eventClass

    @classmethod
    def registerEventInstance(cls, eventInstance: EventMeta):
        cls.__instances[eventInstance.__class__] = eventInstance

    @classmethod
    def getEventClass(cls, className: str) -> Optional[CLASS]:
        return cls.__classes.get(className)

    @classmethod
    def getEventInstance(cls, className: str) -> Optional[EventMeta]:
        eventClass: Optional[CLASS] = cls.getEventClass(className)
        return cls.__instances.get(eventClass) if eventClass is not None else None


class EventMeta(type):
    def __new__(mcs, clsname: str, bases: Tuple[...], namespace: Dict[str, Any], **kwargs) -> CLASS:
        """Create new class object.
        Args:
            clsname: name of the class object
             (This becomes class object's __name__ attribute.)
            bases: tuple of class object's parent classes to define inheritance.
             (This becomes class object's __bases__ attribute.)
            namespace: class object's namespace.
             (This is copied to class object's __dict__ attribute.)
            kwargs: other keyword arguments to process.

        Returns:
            class object created with given class name, parent classes, class namespace.
        """
        cls = super(EventMeta, mcs).__new__(mcs, clsname, bases, namespace)
        EventStorage.registerEventClass(cls)
        return cls

    def __init__(self, *args, **kwargs) -> None:
        """Initialize instance.
        Args:
            args: positional arguments
            kwargs: keyword arguments
        """
        super().__init__(*args, **kwargs)
        EventStorage.registerEventInstance(self)

    def __call__(cls, *args, **kwargs):
        """Singleton design pattern
        Make all Event classes have single instance.

        Args:
            args: positional arguments passed with class call.
            kwargs: keyword arguments passed with class call.

        Returns:
            an instance of Event class which is ensured to be only instance of this event class.
        """
        instance: Optional[EventMeta] = EventStorage.getEventInstance(cls.__name__)
        if instance is not None:
            return instance
        return super().__call__(*args, **kwargs)


class EventException(Exception):
    def __init__(self, event: BaseEvent, msg: Optional[str] = None) -> None:
        self.event = event
        self.msg = (msg if msg is not None
                    else "Unexpected exception has been occured during processing event: {0}".format(event.name))

    def __repr__(self) -> str:
        return "<EventException:event={0}>".format(self.event.name)

    def __str__(self) -> str:
        return "[{}] {}".format(self.__name__, self.msg)

    def getTracebacks(self) -> List:
        return traceback.format_exception(self.__class__, self, self.__traceback__, limit=None)


class ListenerDispatchException(EventException):
    def __init__(self, event: BaseEvent, listener: CoroutineFunction, original: BaseException):
        msg: str = "Listener {0!r} raised exception {1.__class__.__name__} : {1}".format(listener, original)
        super(ListenerDispatchException, self).__init__(event, msg)
        self.listener: CoroutineFunction = listener
        self.original: BaseException = original

    def __repr__(self) -> str:
        return ("<ListenerDispatchException:event={0},listener={1},original={2}>"
                .format(self.event.name, self.listener, self.original))


class BaseEvent(metaclass=EventMeta):

    def __init__(self):
        super(BaseEvent, self).__init__()
        # Parse class name to event's name : 'BaseEvent -> Base'
        self._name = self.__class__.__name__.replace('Event', '')

    @property
    def name(self) -> str:
        return self._name

    async def check(self):
        """Check status to decide whether to dispatch event or not,
        Returns:
            check (bool) : boolean value to do dispatch (True -> dispatch / False -> pass)
        """
        raise NotImplementedError("Event subclasses must define check() method!")
