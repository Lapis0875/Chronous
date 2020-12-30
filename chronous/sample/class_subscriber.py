from chronous.events import BaseEvent, EventBusFactory, EVENT_BUS, EventBus


@EventBusFactory.registerSubclass
class LifecycleBus(EventBus):

    def __init__(self):
        super().__init__(name='lifecycle')
        # parent = EventBusFactory.getBus(name='lifecycle')
        # print(parent.__dict__)
        print(self.__dict__)
        # self.__dict__.update(parent.__dict__)
        # print(self.__dict__)
        self.subclass = True

    def __repr__(self):
        return 'LifecycleBus(name=lifecycle)'

    async def loop(self, count: int = 0):
        if count > 0:
            for i in range(count):
                await self._loop(i)
        else:
            i: int = 0
            while True:
                await self._loop(i)
                i += 1

    async def _loop(self, i: int):
        self.logger.debug('Dispatching {} event')
        await self.dispatch('Loop', loopCount=i)


# You can get same bus object using same name.
lifecycleBus = LifecycleBus()
print(lifecycleBus, id(lifecycleBus), hash(lifecycleBus), lifecycleBus.__dict__)
print(EventBusFactory.getBusNames())
bus2: EVENT_BUS = EventBusFactory.getBus(name='lifecycle')
print(bus2, id(bus2), hash(bus2), bus2.__dict__)
print(lifecycleBus is bus2)


@lifecycleBus.registerEvent
class StartEvent(BaseEvent):
    """
    Lifecycle event indicating 'Start' phase of the process
    """

    text: str = 'Hello Event!'

    def __init__(self):
        super().__init__()

    async def check(self):
        return False    # You need to manually dispatch this.


@lifecycleBus.registerEvent
class LoopEvent(BaseEvent):
    """
    Lifecycle event indicating 'Loop' phase of the process
    """

    loopCount: int = 0

    def __init__(self):
        super().__init__()

    async def check(self):
        return True     # Always dispatched on each loop.


@lifecycleBus.registerEvent
class CloseEvent(BaseEvent):
    """
    Lifecycle event indicating 'Close' phase of the process
    """

    totalLoopCount: int = 0
    farewell: str = 'Good bye!'

    def __init__(self):
        super().__init__()

    async def check(self):
        return False    # You need to manually dispatch this.

print(lifecycleBus.events)
print(lifecycleBus._events)

# Subscribing class
# @lifecycleBus.subscribe
@EventBus.subscribeToBus('lifecycle')
class LifecycleSubscriber:
    loopCount: int = 0

    def __init__(self):
        """
        __init__ cannot have any arguments currently.
        """
        lifecycleBus.logger.debug('Initializing subscriber {}'.format(self.__class__.__name__))
        lifecycleBus.logger.debug('Inspecting metadata: {}'.format(self.__class__.__dict__))
        lifecycleBus.logger.debug('Inspecting listener: {}'.format(self.someStartHandler.__dict__))

    # Add listener using architecture's bus attribute.
    # If you define event listener with parameter 'eventName',
    # listener's name does not need to be 'onEvent' structure.
    @lifecycleBus.listen(eventName='Start')
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

    @lifecycleBus.listen(eventName='Close')
    async def closingApp(self, e: CloseEvent):
        print(e.totalLoopCount)
        print(e.totalLoopCount == self.loopCount)   # Accessing to subscriber class's attribute!
        print(e.farewell)


async def task():
    await lifecycleBus.dispatch('Start', text='')
    for i in range(5):
        await lifecycleBus.dispatch('Loop', loopCount=i, extra='Looping for {} times!'.format(i))
    await lifecycleBus.dispatch('Close', totalLoopCount=i, farewell='Finishing example!')
