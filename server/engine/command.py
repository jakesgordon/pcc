from enum import Enum
from dataclasses import dataclass

@dataclass
class Command:
    pass

@dataclass
class OpenCommand(Command):
    def __init__(self, target):
        self.target = target

@dataclass
class CloseCommand(Command):
    def __init__(self, target):
        self.target = target

@dataclass
class UnlockCommand(Command):
    def __init__(self, target, using):
        self.target = target
        self.using  = using

@dataclass
class TakeCommand(Command):
    def __init__(self, target):
        self.target = target

Command.Open   = OpenCommand
Command.Close  = CloseCommand
Command.Unlock = UnlockCommand
Command.Take   = TakeCommand
