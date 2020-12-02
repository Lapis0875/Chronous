# Chronous

![py_ver](https://img.shields.io/pypi/pyversions/chronous?label=Python%20Version&logo=python&logoColor=yellow)

![license](https://img.shields.io/github/license/Lapis0875/chronous?logo=github&logoColor=white)
![issues](https://img.shields.io/github/issues/Lapis0875/Chronous?logo=github&logoColor=white)

![pypi_ver](https://img.shields.io/pypi/v/chronous?logo=pypi&logoColor=blue)
![pypi_package](https://img.shields.io/pypi/format/chronous?label=package&logo=pypi)
![pypi_status](https://img.shields.io/pypi/status/chronous?color=blue&logo=pypi&logoColor=blue)

![discord](https://img.shields.io/discord/622434051365535745?color=blue&label=Discord&logo=Discord&logoColor=White)


Chronous is a asynchronous python library designed to make asynchronous event-driven architectures.
Inspired by discord.py and Minecraft Bukkit's event system.

## Examples
### 1. Simple architecture implementation.
```python
# Sample source code in chronous/sample/simple_architecture.py
from __future__ import annotations
import asyncio
from typing import NoReturn
from chronous.Architecture import BaseArchitecture
from chronous.events import BaseEvent, DefaultBus


class StartEvent(BaseEvent):

    def __init__(self):
        super().__init__()
        self.text: str = "UNDEFINED"

    async def check(self):
        pass


class CloseEvent(BaseEvent):

    def __init__(self):
        super().__init__()
        self.index: int = 0

    async def check(self):
        pass


class SampleArchitecture(BaseArchitecture):

    def __init__(self) -> None:
        super(SampleArchitecture, self).__init__(name="sample", bus=DefaultBus)

        # Registering events
        self.bus.registerEvent(event=StartEvent())
        self.bus.registerEvent(event=CloseEvent())

    def run(self) -> None:
        # Registering default lifecycle events
        # Start process.
        print("Starting process...")
        asyncio.run(self.process())

    async def process(self) -> NoReturn:
        print('='*20)
        await self.bus.dispatch("start", text="Hello Event!")
        index: int = 0
        while index < 10:
            print("Looping!")
            index += 1
        await self.bus.dispatch("close", index=10)
        print('='*20)


sample = SampleArchitecture()


# Multiple listener sample
@sample.bus.listen
async def onStart(e: StartEvent):
    print('{name} phase - listener 1'.format(name=e.name))
    print('event argument : text = {}'.format(e.text))


@sample.bus.listen
async def onStart(e: StartEvent):
    print('{name} phase - listener 2'.format(name=e.name))
    print('event  : {}'.format(e))


# Exception sample
@sample.bus.listen
async def onClose(e: CloseEvent):
    print('{name} phase - listener 1'.format(name=e.name))
    print('event argument : index = {}'.format(e.index))
    print(e.__dict__)
    print('Closing process...')
    print(1/0)  # Making an error to test dispatch exception

sample.run()
```

### 2. Class subscriber implementation.
```python
# Sample source code in chronous/sample/class_subscriber.py
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
```