from typing import Type, List, Coroutine, Any
from .Event import BaseEvent, EVENT


class Dispatcher:
    def __init__(self, target_event: EVENT):
        self.event = target_event
        self.name: str = target_event.name
        self.listeners: List[Coroutine] = []
