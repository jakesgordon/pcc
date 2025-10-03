from enum import Enum
from dataclasses import dataclass

@dataclass
class Event:
    pass

@dataclass
class OpenedEvent(Event):
    def __init__(self, target):
        self.target = target

@dataclass
class ClosedEvent(Event):
    def __init__(self, target):
        self.target = target

@dataclass
class UnlockedEvent(Event):
    def __init__(self, target, using):
        self.target = target
        self.using = using

@dataclass
class TakenEvent(Event):
    def __init__(self, target):
        self.target = target

Event.Opened   = OpenedEvent
Event.Closed   = ClosedEvent
Event.Unlocked = UnlockedEvent
Event.Taken    = TakenEvent
