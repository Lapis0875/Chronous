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
