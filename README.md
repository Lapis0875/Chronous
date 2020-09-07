# Chronous
![pypi](https://img.shields.io/pypi/pyversions/chronous?label=Python&logo=python&logoColor=yellow)
![format](https://img.shields.io/pypi/format/chronous?label=package-format&logo=pypi)
![discord](https://img.shields.io/discord/622434051365535745?color=blue&label=Discord&logo=Discord&logoColor=White)
![release](https://img.shields.io/github/release-date/Lapis0875/Chronous)

Chronous is a asynchronous python library designed to make asynchronous event-driven architectures on discord.py

[Example]
```python
import asyncio
from typing import NoReturn
from chronous.Architecture import BaseArchitecture
from chronous.events.LifecycleEvents import *


class SampleArchitecture(BaseArchitecture):

    def __init__(self) -> None:
        super(SampleArchitecture, self).__init__(game_name="sample")

        # Registering events
        self.registerEvent(event=Setup())
        self.registerEvent(event=Init())
        self.registerEvent(event=Start())
        self.registerEvent(event=Close())

    def run(self) -> None:
        # Registering default lifecycle events
        # Start the game.
        print("Starting process...")
        asyncio.run(self.process())

    async def process(self) -> NoReturn:
        await self.dispatch("setup")
        await self.dispatch("init")
        print('='*20)
        await self.dispatch("start", datetime.datetime.now())
        index: int = 0
        while index < 10:
            print("Looping!")
            index += 1
        await self.dispatch("close")
        print('='*20)


sample = SampleArchitecture()


# Multiple listener sample
@sample.listen()
async def setup(ec: EventContext):
    print("{ec.name} phase - listener 1".format(ec=ec))


@sample.listen()
async def setup(ec: EventContext):
    print("{ec.name} phase - listener 2".format(ec=ec))


# EventContext  sample
@sample.listen()
async def init(ec: EventContext):
    print("Initialization phase")
    print("Event : {ec.event}".format(ec=ec))


# Additional arguments sample
@sample.listen()
async def start(ec: EventContext, time: datetime):
    print("Starting process...")
    print(f"Starting at : {time}")


# Exception sample
@sample.listen()
async def close(ec: EventContext):
    print("Closing process...")

sample.run()

```
