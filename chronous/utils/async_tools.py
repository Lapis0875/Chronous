from __future__ import annotations

import asyncio
from typing import Iterable, Generator, AsyncIterator
from .type_hints import T


class AsyncIter:
    def __init__(self, items: Iterable[T]):
        self.items: Generator = (item for item in items)

    def __aiter__(self) -> AsyncIterator[T]:
        return self

    async def __anext__(self) -> T:
        try:
            value: T = next(self.items)
        except StopIteration:
            raise StopAsyncIteration
        return value
        # except GeneratorExit:
        #     raise StopAsyncIteration
