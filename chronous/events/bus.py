from __future__ import annotations
import asyncio
import inspect
from copy import deepcopy
from functools import reduce
from typing import Dict, List, Optional, Union, Tuple, Any
from .event import BaseEvent, ListenerDispatchException
from chronous.utils import CoroutineFunction, CLASS, getLogger, Logger, LogLevels, AsyncIter

__all__ = (
    "BusMeta",
    "EventBus",
    "DefaultBus"
)


class BusMeta(type):
    """
    Ensure only one EventBus instance can be made with a certain name. (이름당 한개의 이벤트 버스를 보장)
    """
    _buses: Dict[str, EventBus] = {}

    def __init__(self, *args, **kwargs):
        """Make bus objects able to be instantiate once per name
        (이름당 한개의 이벤트 버스만 생성되게 함)

        Args:
            args (Any):
            kwargs (Any):

        Returns:
            bus (EventBus) :
        """
        name: str = kwargs.get('name')
        bus = self._buses.get(name)
        if bus is None:
            super(BusMeta, self).__init__(*args, **kwargs)
        else:
            self = bus


class EventBus(metaclass=BusMeta):
    """Bus class of Events.

    Attributes:
        name (str): name of this event bus.
        events (List[BaseEvent]): list of events registered in this bus.
        eventLoop (asyncio.AbstractEventLoop): event loop which this bus is using.
    """
    _events: Dict[str, BaseEvent]
    _listeners: Dict[BaseEvent, List[CoroutineFunction]]
    _subscribers: Dict[str, object]

    def __init__(self, *, name: str):
        self.logger: Logger = getLogger('chronous.events.bus', LogLevels.DEBUG)
        self._name = name
        self._event_loop = asyncio.get_event_loop()

        self._events: Dict[str, BaseEvent] = {}
        self._listeners: Dict[BaseEvent, List[CoroutineFunction]] = {}
        self._subscribers: Dict[str, object] = {}

    def __repr__(self):
        return '<EventBus: name={}>'.format(self.name)

    @property
    def name(self) -> str:
        return self._name

    @property
    def eventLoop(self) -> asyncio.AbstractEventLoop:
        return self._event_loop

    @property
    def events(self) -> Tuple[BaseEvent]:
        return tuple(self._events.values())

    def registerEvent(self, event: BaseEvent):
        self.logger.debug('Checking parameter `event` : {}'.format(event))
        if isinstance(event, BaseEvent):
            self.logger.debug('Registering event {} to this bus'.format(event.name))
            self._events[event.name.lower()] = event
            self._listeners[event] = []
        else:
            raise TypeError(
                'Parameter "event" must be an instance of BaseEvent`s subclasses, not {}'
                    .format(type(event))
            )

    def subscribe(self, subscriber: CLASS):
        """Subscribe listeners from subscriber class.

        Args:
            subscriber (class) : class object to subscribe event bus.
        """
        if inspect.isclass(subscriber):

            setattr(subscriber, '__subscriber__', True)
            events: List[str] = []

            listeners = filter(lambda m: inspect.ismethod(m) and m.__listener__, subscriber.__dict__.items())
            for method in listeners:
                eventName: Optional[str] = getattr(method, '__event_name__', None)
                if eventName is None:
                    raise AttributeError(
                        'Malformed listener {} in subscriber {} does not have metadata "__event_name__"'
                        .format(method.__name__, subscriber.__name__)
                    )

                # Checking if event is existing and registered.
                event: Optional[BaseEvent] = self._events.get(eventName)
                if event is None:
                    raise AttributeError(
                        'Malformed listener {} in subscriber {} has event not registered in the bus {}'
                        .format(method.__name__, subscriber.__name__, self.__name__)
                    )
                events.append(eventName)
            setattr(subscriber, '__subscribing_events__', events)
            self._subscribers[subscriber.__name__] = subscriber()
        else:
            raise TypeError('Argument "subscriber" must be a class object!')

    def listen(self, eventName: Optional[str] = None):
        """Add listener to event.

        Args:
            eventName (Optional[str]): event name to register this listener
        """

        def registerListener(listener: CoroutineFunction):
            """Add listener to event.

            Args:
                listener (coroutine function): coroutine function to register as listener
            """
            if not asyncio.iscoroutinefunction(listener):
                raise TypeError('listener must be a coroutine function object!')

            # print(type(listener), '{!r}'.format(listener))
            # print(listener.__name__)
            # print(listener.__qualname__)
            # print(listener.__annotations__)

            eventNameParsed: str = (
                eventName.lower()
                if eventName is not None
                else listener.__name__.replace('on', '').lower()
            )
            self.logger.debug('event name = {}'.format(eventNameParsed))
            event: Optional[BaseEvent] = self._events.get(eventNameParsed)
            self.logger.debug('event = {}'.format(event))
            if event is None:
                raise ValueError('Event named {} does not exist!'.format(eventNameParsed))
            try:
                self._listeners[event].append(listener)
            except KeyError:
                raise ValueError('Event named {} does not reigstered in this bus!'.format(eventNameParsed))
            # Metadata of listener
            setattr(listener, '__listener__', True)
            setattr(listener, '__event_name__', event.name)

        return registerListener

    async def dispatch(self, event: Union[BaseEvent, str], **attrs):
        """Dispatch the event.
        Call all registered listeners with given parameters.

        Args:
            event: An event instance or string value of event's name
        """
        if isinstance(event, str):
            eventName: str = event
            event = self._events.get(event)
            if event is None:
                raise ValueError('Event named {} does not exist!'.format(eventName))

        self.logger.debug('event before patching : {}'.format(event.__dict__))
        copied: Dict[str, Any] = deepcopy(event.__dict__)
        # Event patching
        for name, value in attrs.items():
            setattr(event, name, value)
        self.logger.debug('event after patching : {}'.format(event.__dict__))

        listeners = self._listeners.get(event)
        self.logger.debug('listeners : {}'.format(listeners))
        self.logger.debug('Dispatching all subscribers')

        results = await asyncio.gather(
            # functions
            *map(
                # i_coro = (i, coro)
                lambda i_coro: asyncio.create_task(
                    i_coro[1](event),
                    name='dispatch_{event}_{index}'
                    .format(event=event.name, index=i_coro[0])
                ),
                enumerate(filter(lambda l: l.__name__ == l.__qualname__, listeners))
            ),
            # methods
            *map(
                # i_coro = (i, coro)
                lambda i_coro: asyncio.create_task(
                    i_coro[1](
                        self._subscribers[i_coro[1].__qualname__.split('.')[0]]
                        ,event
                    ),
                    name='dispatch_{event}_{index}'
                    .format(event=event.name, index=i_coro[0])
                ),
                enumerate(filter(lambda l: l.__name__ != l.__qualname__, listeners))
            ),
            return_exceptions=True
        )

        self.logger.debug('Event:{event} - Dispatch results : {results}'.format(event=event.name, results=results))
        for i, result in enumerate(results):
            self.logger.debug(
                'Event:{event} - Dispatch {index} result : {result}'.format(
                    event=event.name,
                    index=i,
                    result=result
                )
            )
            if isinstance(result, Exception):
                self.logger.debug(
                    'Found Exception on the result of dispatch {0}. Raising ListenerException...'.format(i))
                raise ListenerDispatchException(event=event, listener=listeners[i], original=result)

        # Reset event data
        event.__dict__ = copied

    async def loop(self):
        async for event in AsyncIter(self._events.values()):
            doDispatch: bool = await event.check()
            if doDispatch:
                await self.dispatch(event)


DefaultBus: EventBus = EventBus(name='Default')
