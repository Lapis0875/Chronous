from __future__ import annotations
from collections import AsyncIterator
from typing import Any, Iterable


class AsyncIter(AsyncIterator):
    def __init__(self, items: Iterable[Any]):
        self.items = (i for i in items)

    def __aiter__(self) -> AsyncIter:
        return self

    def __anext__(self) -> Any:
        try:
            yield self.items
        except GeneratorExit:
            raise StopAsyncIteration
