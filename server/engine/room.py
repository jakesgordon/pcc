import json

from enum import Enum
from result import Ok, Err

from .command import Command
from .event import Event
from .item import Item, Items
from .relationship import Relationship

class Room:

    def __init__(self, name, description, items, relationships):
        self.name = name
        self.description = description
        self.items = items
        self.items.add(Item(
            name="room",
            description=self.description,
            traits=[]
        ))
        self.events = []
        self.inventory = []

        for relationship in relationships:
            item = self.items.get(relationship.source)
            item.append(relationship.target, relationship.kind)

    #--------------------------------------------------------------------------

    def item(self, name):
        return self.items.get(name)

    #--------------------------------------------------------------------------

    def facts(self, name="room"):
        facts = []
        children = []
        item = self.item(name)
        facts.append(f"The [{name}] can be described as '{item.description}'")
        if item.is_closed:
            facts.append(f"The [{name}] is closed")
        if item.is_open:
            facts.append(f"The [{name}] is open")
        if item.is_container and len(item.contains) == 0:
            facts.append(f"The [{name}] is empty")
        if item.is_locked:
            facts.append(f"The [{name}] is locked")
        for child in item.has:
            facts.append(f"The [{name}] has a [{child}]")
            if not child in children:
                children.append(child)
        if not item.is_closed:
            for child in item.contains:
                facts.append(f"The [{name}] contains a [{child}]")
                if not child in children:
                    children.append(child)
        for c in children:
            facts.extend(self.facts(c))
        return facts

    #--------------------------------------------------------------------------

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

    #--------------------------------------------------------------------------

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

    #--------------------------------------------------------------------------

    @staticmethod
    def load(filename):
        return Room.from_json(json.load(open(filename)))

    @staticmethod
    def from_json(data):
        name = data.get("name")
        description = data.get("description")

        assert name is not None
        assert description is not None

        items = Items()
        for i in data.get("items", []):
            items.add(Item(
                name=i.get("name"),
                description=i.get("description"),
                traits=[Item.Trait(t) for t in i.get("traits", [])]
            ))

        relationships = []
        for r in data.get("relationships", []):
            relationships.append(Relationship(
                kind=Relationship.Kind(r.get("relationship") or r.get("kind")),
                source=r.get("source"),
                target=r.get("target")
            ))

        return Room(
            name=name,
            description=description,
            items=items,
            relationships=relationships,
        )

    #--------------------------------------------------------------------------
