import json

from enum import Enum
from result import Ok, Err

from .command import Command
from .event import Event
from .item import Item, Items
from .relationship import Relationship, Relationships

#------------------------------------------------------------------------------

class Room:
    def __init__(self, name, description, items, relationships):
        self.name = name
        self.description = description
        self.items = items
        self.relationships = relationships
        self.items.add(Item(
            name="room",
            description=self.description,
            traits=[]
        ))
        self.events = []
        self.inventory = []

    def item(self, name):
        return self.items.get(name)

    def facts(self, name="room"):
        facts = []
        children = []
        item = self.item(name)
        facts.append(f"The [{name}] can be described as '{item.description}'")
        if item.is_closed:
            facts.append(f"The [{name}] is closed")
        if item.is_open:
            facts.append(f"The [{name}] is open")
        # if self.relationships.is_empty(item):
        #     facts.append(f"The [{name}] is empty")
        if item.is_locked:
            facts.append(f"The [{name}] is locked")
        for r in self.relationships:
            if r.source == name:
                match r.kind:
                    case Relationship.Kind.HAS:
                        facts.append(r.fact)
                        if not r.target in children:
                            children.append(r.target)

                    case Relationship.Kind.CONTAINS:
                        if not item.is_closed:
                            facts.append(r.fact)
                            if not r.target in children:
                                children.append(r.target)

        for c in children:
            facts.extend(self.facts(c))
        return facts

    def execute(self, command):
        match command:
            case Command.Open():
                item = self.item(command.target)
                return self.record(item.open())
            case Command.Take():
                item = self.item(command.target)
                return self.record(item.take())
            case _:
                raise TypeError(f"expected Command, but got {type(command)}")

    def record(self, result):
        if isinstance(result, Ok):
            self.record(result.unwrap())
        elif isinstance(result, Err):
            pass
        elif isinstance(result, Event):
            self.events.append(result)
        elif isinstance(result, list):
            self.events.extend(result)
        return result

    @staticmethod
    def from_json(data):
        return Room(
            name=data.get("name"),
            description=data.get("description"),
            items=Items.from_json(data.get("items", [])),
            relationships=[Relationship.from_json(r) for r in data.get("relationships", [])]
        )

    @staticmethod
    def load(filename):
        return Room.from_json(json.load(open(filename)))

#------------------------------------------------------------------------------
