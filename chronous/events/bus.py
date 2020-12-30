from __future__ import annotations
import asyncio
import inspect
from copy import deepcopy
from typing import Dict, List, Optional, Union, Tuple, Any, ClassVar, TypeVar
from .event import BaseEvent, ListenerDispatchException
from chronous.utils.type_hints import CoroutineFunction, CLASS
from chronous.utils.logging_util import getLogger, Logger, LogLevels
from chronous.utils.module_private import modulePrivate, ModulePrivateError
from chronous.utils import AsyncIter, isMethodFunction, notMethodFunction

__all__ = (
    "EventBusFactory",
    "EVENT_BUS",
    "EventBus",
    "DefaultBus"
)


class EventBusFactory:
    _bus_cache: ClassVar[Dict[str, EVENT_BUS]] = {}
    _subclass_cache: ClassVar[Dict[str, CLASS]] = {}
    _logger: ClassVar[Logger] = getLogger('chronous.events.busfactory')

    @classmethod
    def getBus(cls, name: str, subclass: Optional[str] = None) -> EVENT_BUS:
        cls._logger.debug('Retrieve bus instance named {}.'.format(name))
        try:
            return cls._bus_cache[name]
        except KeyError:
            cls._logger.debug('No bus named {} is in cache. Create new one.'.format(name))
            if subclass is not None:
                try:
                    subclass: CLASS = cls._subclass_cache[subclass]
                    cls._logger.debug('Create bus with subclass named {}.'.format(subclass.__name__))
                    return cls.createBus(name, subclass)
                except:
                    cls._logger.debug(
                        'No subclass named {} registered in EventBusFactory. Raise KeyError.'
                        .format(subclass)
                    )
                    raise KeyError('No subclass named {} registered in EventBusFactory.'.format(subclass))

    @classmethod
    def getRegisteredBus(cls, name: str) -> Optional[EVENT_BUS]:
        cls._logger.debug('Retrieve bus instance named {} from cache.'.format(name))
        return cls._bus_cache.get(name)

    @classmethod
    @modulePrivate
    def createBus(cls, name: str, Class: Optional[CLASS] = None):
        cls._logger.debug(
            'Create new bus instance named {} with Class '
            .format(
                name,
                Class.__name__ if Class is not None else 'EventBus'
            )
        )
        if Class is not None:
            __init__argspec = inspect.getfullargspec(Class.__init__)
            print(__init__argspec)
            bus = Class(name)
        else:
            bus = EventBus(name=name)
        cls._bus_cache[name] = bus
        return bus

    @classmethod
    def getBusNames(cls) -> Tuple[str, ...]:
        return tuple(cls._bus_cache.keys())

    @classmethod
    def registerSubclass(cls, subclass: CLASS) -> CLASS:
        """Register Subclass of EventBus and make them can be instantiated through factory/
        Args:
            subclass (class object): Class subclassing EventBus.
        """
        cls._logger.debug('Register EventBus subclass named {}.'.format(subclass.__name__))
        if not issubclass(subclass, EventBus):
            raise TypeError(
                'Only subclass of EventBus can be registered as subclass on EventBusFactory. {} is not suitable.'
                .format(subclass)
            )
        print(cls.__init__)
        argspec: inspect.FullArgSpec = inspect.getfullargspec(cls.__init__)
        print(argspec)
        args: List[str] = argspec.args
        kwonlyargs: List[str] = argspec.kwonlyargs
        defaults = argspec.defaults
        if len(args) == 1:
            pass
        else:
            pass

        cls._subclass_cache[subclass.__name__] = subclass
        return subclass     # Return this for later use.

    @classmethod
    @modulePrivate
    def registerInstance(cls, instance: EventBus):
        cls._bus_cache[instance.name] = instance


# Private class. Type hint is supported using EVENT_BUS TypeVar.
# 굳이 EventBus가 하나의 이름에 고유한 객체를 가져야 할까? 너무 강박적으로 싱글톤처럼 만드려 하는것 같다.
@modulePrivate
class EventBus:
    """Bus class of Events.

    Properties:
        name (str): name of this event bus.
        events (List[BaseEvent]): list of events registered in this bus.
        eventLoop (asyncio.AbstractEventLoop): event loop which this bus is using.
    """

    _events: Dict[str, BaseEvent]
    _listeners: Dict[BaseEvent, List[CoroutineFunction]]
    _subscribers: Dict[str, object]

    def __call__(self, *args, **kwargs):
        name = kwargs.get('name')
        bus: Optional[EVENT_BUS] = EventBusFactory.getRegisteredBus(name)
        if bus is not None:
            return bus

    def __init__(self, *, name: str):
        """Make bus objects able to be instantiate once per name
        (이름당 한개의 이벤트 버스만 생성되게 함)

        Args:

        Returns:
            bus (EventBus) :
        """
        if EventBusFactory.getRegisteredBus(name) is None:
            self.logger: Logger = getLogger('chronous.events.bus', LogLevels.DEBUG)
            self._name = name
            self._event_loop = asyncio.get_event_loop()

            self._events: Dict[str, BaseEvent] = {}
            self._listeners: Dict[BaseEvent, List[str]] = {}
            self._subscribers: Dict[str, object] = {}
            EventBusFactory.registerInstance(self)
        else:
            raise ValueError('Cannot instantiate already existing event bus.')

    def __repr__(self):
        return '<EventBus: name={}>'.format(self._name)

    @property
    def name(self) -> str:
        return self._name

    @property
    def eventLoop(self) -> asyncio.AbstractEventLoop:
        return self._event_loop

    @property
    def events(self) -> Tuple[BaseEvent, ...]:
        return tuple(self._events.values())

    def registerEvent(self, event: Union[BaseEvent, CLASS]):
        self.logger.debug('Checking parameter `event` : {}'.format(event))
        if isinstance(event, BaseEvent):
            self.logger.debug('Registering event {} to this bus'.format(event.name))
            self._events[event.name.lower()] = event
            self._listeners[event.name] = []
        elif inspect.isclass(event):
            if issubclass(event, BaseEvent):
                self.logger.debug('Register event with event class {}\n{}'.format(event.__qualname__, event.__dict__))
                instance = event()
                self.registerEvent(instance)
                return event
            else:
                raise TypeError('Event class "{}" must subclass "BaseEvent"'.format(event.__qualname__))
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
        print('Registering subscriber {}'.format(subscriber.__qualname__))
        if inspect.isclass(subscriber):

            setattr(subscriber, '__subscriber__', True)
            events: List[str] = []

            print(subscriber.__dict__)

            listeners = filter(
                    lambda attr: getattr(attr, '__listener__', False),
                    subscriber.__dict__.values()
            )
            for method in listeners:
                print(method)
                print(method.__qualname__)
                print(method.__dict__)
                eventName: Optional[str] = getattr(method, '__event_name__', None)
                print('__event_name__ =', eventName)
                if eventName is None:
                    raise AttributeError(
                        'Malformed listener {} in subscriber {} does not have metadata "__event_name__"'
                        .format(method.__name__, subscriber.__name__)
                    )

                # Checking if event is existing and registered.
                event: Optional[BaseEvent] = self._events[eventName]
                print('event =', event)
                if event is None:
                    raise AttributeError(
                        'Malformed listener {} in subscriber {} has event not registered in the bus {}'
                        .format(method.__name__, subscriber.__name__, self._name)
                    )
                events.append(eventName)
            setattr(subscriber, '__subscribing_events__', events)
            self._subscribers[subscriber.__name__] = subscriber()
        else:
            raise TypeError('Argument "subscriber" must be a class object!')

    # Just use EventBus instance.
    @classmethod
    def subscribeToBus(cls, busName: str):
        bus: Optional[EventBus] = EventBusFactory.getBus(busName)
        if bus is None:
            raise ValueError('bus named {} does not exist'.format(busName))

        def registerSubscriber(subscriber: CLASS):
            return bus.subscribe(subscriber)

        return registerSubscriber

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
            print('Registering listener {}'.format(listener.__qualname__))
            if not asyncio.iscoroutinefunction(listener):
                raise TypeError('listener must be a coroutine function object!')

            # print(type(listener), '{!r}'.format(listener))
            # print(listener.__name__)
            # print(listener.__qualname__)
            # print(listener.__annotations__)

            eventNameParsed: str = (
                listener.__name__.replace('on', '').lower()
                if eventName is None
                else eventName.lower()
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
            print(listener.__dict__)
            return listener

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
                enumerate(filter(notMethodFunction, listeners))
            ),
            # method functions
            *map(
                # i_coro = (i, coro)
                lambda i_coro: asyncio.create_task(
                    i_coro[1](
                        self._subscribers[i_coro[1].__qualname__.split('.')[0]]
                        , event
                    ),
                    name='dispatch_{event}_{index}'
                    .format(event=event.name, index=i_coro[0])
                ),
                enumerate(filter(isMethodFunction, listeners))
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

    async def infiniteLoop(self):
        while True:
            await self._loop()

    async def loop(self, count: int = 0):
        for _ in range(count):
            await self._loop()

    async def _loop(self):
        """Tasks to await during each loop."""
        async for event in AsyncIter(filter(lambda e: e.check(), self._events.values())):
            self.logger.debug('Checking {} event to be dispatched through loop...'.format(event.name))
            doDispatch: bool = await event.check()
            if doDispatch:
                self.logger.debug(' events to be dispatched through loop...')
                await self.dispatch(event)


EVENT_BUS = TypeVar('EVENT_BUS', bound=EventBus)
DefaultBus: EVENT_BUS = EventBus(name='Default')
