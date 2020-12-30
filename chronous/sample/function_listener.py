from __future__ import annotations
import asyncio
from chronous.events import BaseEvent, DefaultBus


@DefaultBus.registerEvent
class StartEvent(BaseEvent):

    def __init__(self):
        super().__init__(loopable=False)
        self.text: str = "UNDEFINED"


@DefaultBus.registerEvent
class LoopEvent(BaseEvent):

    loopCount: int

    def __init__(self):
        super().__init__(loopable=True)


@DefaultBus.registerEvent
class CloseEvent(BaseEvent):

    def __init__(self):
        super().__init__(loopable=False)
        self.farewell: str = "Good bye!"


# Multiple listener sample
@DefaultBus.listen
async def onStart(e: StartEvent):
    print('{name} phase - listener 1'.format(name=e.name))
    print('event argument : text = {}'.format(e.text))


@DefaultBus.listen
async def onStart(e: StartEvent):
    print('{name} phase - listener 2'.format(name=e.name))
    print('event  : {}'.format(e))


# When decorator argument is specified, listener's name is not forced to 'onEvent' format.
@DefaultBus.listen('Loop')
async def someLoopListener(e: LoopEvent):
    print('{} phase - looping {}'.format(e.name, e.loopCount))
    print('event  : {}'.format(e.__dict__))


# Exception sample
@DefaultBus.listen
async def onClose(e: CloseEvent):
    print('{name} phase - listener 1'.format(name=e.name))
    print('event argument defined in event class : farewell = {}'.format(e.farewell))
    print('event argument not defined in event class and patched : totalCount = {}'.format(e.totalCount))
    print(e.__dict__)
    print('Closing process...')
    print(1/0)  # Making an error to test dispatch exception


async def main():
    await DefaultBus.dispatch('Start', text="Starting main coroutine!")
    await DefaultBus.loop(5)
    await DefaultBus.dispatch('Start', farewell="Ending main coroutine!", totalCount=5)


asyncio.get_event_loop().run_until_complete(main())

