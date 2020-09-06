import asyncio
from typing import NoReturn

from chronous.Architecture import BaseArchitecture
from chronous.events.LifecycleEvents import *


class SampleArchitecture(BaseArchitecture):

    def __init__(self) -> None:
        super(SampleArchitecture, self).__init__(game_name="sample")

        self.registerEvent(event=Setup())
        self.registerEvent(event=Init())
        self.registerEvent(event=Close())

    def run(self) -> None:
        # Setup the game.
        # Registering default lifecycle events
        # Start the game.
        print("Starting process...")
        asyncio.run(self.process())

    async def process(self) -> NoReturn:
        await self.dispatch("setup")
        await self.dispatch("init")
        print("Starting process...")
        index: int = 0
        while index < 10:
            print("Looping!")
            index += 1
        print("Finished process!")
        await self.dispatch("close")


sample = SampleArchitecture()


@sample.listen()
async def setup(ec: EventContext):
    print("Setup phase")
    print(ec.event)


@sample.listen()
async def init(ec: EventContext):
    print("Initialization phase")
    print(ec.event)


@sample.listen()
async def close(ec: EventContext):
    print("Close phase")
    print(ec.event)

sample.run()