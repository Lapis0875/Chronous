from typing import NoReturn

from chronous.events import BaseEvent, EventBus
from chronous import BaseArchitecture

lifecycleBus: EventBus = EventBus(name='lifecycle')


class StartEvent(BaseEvent):
    """
    Lifecycle event indicating 'Start' phase of the process
    """

    text: str = 'Hello Event!'

    def __init__(self):
        super(StartEvent, self).__init__()

    async def check(self):
        return False    # You need to manually dispatch this.


class LoopEvent(BaseEvent):
    """
    Lifecycle event indicating 'Loop' phase of the process
    """

    loopCount: int = 0

    def __init__(self):
        super(LoopEvent, self).__init__()

    async def check(self):
        return True     # Always dispatched on each loop.


class CloseEvent(BaseEvent):
    """
    Lifecycle event indicating 'Close' phase of the process
    """

    totalLoopCount: int = 0
    farewell: str = 'Good bye!'

    def __init__(self):
        super(CloseEvent, self).__init__()

    async def check(self):
        return False    # You need to manually dispatch this.


class LifecycleArchitecture(BaseArchitecture):

    def __init__(self):
        super(LifecycleArchitecture, self).__init__(name='lifecycle', bus=lifecycleBus)
        self.bus.registerEvent(StartEvent())
        self.bus.registerEvent(LoopEvent())
        self.bus.registerEvent(CloseEvent())

    async def process(self) -> NoReturn:
        # dispatching with event attribute
        await self.bus.dispatch('start', text='I`m StartEvent, dispatched manually!')
        for i in range(1, 11):
            # Sample loop
            # dispatching with event attribute & additional attribute
            await self.bus.dispatch('loop', loopCount=i, extra='Lorem ipsum')
        # dispatching with event attribute
        await self.bus.dispatch('close', totalLoopCount=i, farewell='Finishing example. Make your own!')


app = LifecycleArchitecture()


# Subscribing class
@lifecycleBus.subscribe
class LifecycleSubscriber:
    loopCount: int = 0

    def __init__(self):
        """
        __init__ cannot have any arguments currently.
        """
        print(type(self.someStartHandler), self.someStartHandler)
        pass

    # Add listener using architecture's bus attribute.
    # If you define event listener with parameter 'eventName',
    # listener's name does not need to be 'onEvent' structure.
    @app.bus.listen(eventName='start')
    async def someStartHandler(self, e: StartEvent):
        print(e.text)           # Accessing to event object!
        print(getattr(lifecycleBus, '_subscribers', []))

    # Add listener using bus instance variable.
    # If you define event listener without parameter 'eventName',
    # listener's name must be 'onEvent' structure.
    @lifecycleBus.listen()
    async def onLoop(self, e: LoopEvent):
        print('Currently looping {} times'.format(e.loopCount))
        self.loopCount = e.loopCount   # Accessing to subscriber class's attribute!
        print(e.__dict__)
        print(e.extra)     # Attribute not defined in event class, but patched in event object.

    @lifecycleBus.listen(eventName='close')
    async def closingApp(self, e: CloseEvent):
        print(e.totalLoopCount)
        print(e.totalLoopCount == self.loopCount)   # Accessing to subscriber class's attribute!
        print(e.farewell)


app.run()
