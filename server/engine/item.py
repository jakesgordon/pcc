from enum import Enum
from result import Ok, Err
from .event import Event

class Item:
    class Trait(Enum):
        TAKEABLE   = "takeable"      # can be taken by the player (inventory)
        OPENABLE   = "openable"      # can be opened
        CLOSABLE   = "closable"      # can be closed
        LOCKABLE   = "lockable"      # can be locked
        UNLOCKABLE = "unlockable"    # can be unlocked
        CONTAINER  = "container"     # holds items inside
        SUPPORTER  = "supporter"     # items rest on top
        READABLE   = "readable"      # has text to read
        WEARABLE   = "wearable"      # can put on/take off
        EDIBLE     = "edible"        # can be consumed
        TAKEN      = "taken"         # IS taken (inventory)
        CLOSED     = "closed"        # IS closed
        LOCKED     = "locked"        # IS locked

    def __init__(self, name, description = None, traits = None):
        self.name = name
        self.description = description
        self.traits = set(traits or [])

    def has_trait(self, trait):
        return trait in self.traits

    def add_trait(self, trait):
        self.traits.add(trait)

    def remove_trait(self, trait):
        self.traits.discard(trait)

    @property
    def is_takeable(self):
        return self.has_trait(Item.Trait.TAKEABLE)

    @property
    def is_openable(self):
        return self.has_trait(Item.Trait.OPENABLE)

    @property
    def is_closable(self):
        return self.has_trait(Item.Trait.CLOSABLE)

    @property
    def is_lockable(self):
        return self.has_trait(Item.Trait.LOCKABLE)

    @property
    def is_container(self):
        return self.has_trait(Item.Trait.CONTAINER)

    @property
    def is_taken(self):
        return self.is_takeable and self.has_trait(Item.Trait.TAKEN)

    @property
    def is_open(self):
        return (self.is_openable or self.is_closable or self.is_container) and not self.has_trait(Item.Trait.CLOSED)

    @property
    def is_closed(self):
        return (self.is_openable or self.is_closable) and self.has_trait(Item.Trait.CLOSED)

    @property
    def is_locked(self):
        return self.has_trait(Item.Trait.LOCKED)

    def take(self):
        if not self.is_takeable:
            return Err(f"[{self.name}] is not takeable")
        elif self.is_taken:
            return Err(f"[{self.name}] has already been taken")
        else:
            self.add_trait(Item.Trait.TAKEN)
            return Ok(Event.Taken(target=self.name))

    def open(self):
        if not self.is_openable:
            return Err(f"[{self.name}] is not openable")
        elif not self.is_closed:
            return Err(f"[{self.name}] is already open")
        else:
            self.remove_trait(Item.Trait.CLOSED)
            return Ok(Event.Opened(target=self.name))

    def close(self):
        if not self.is_closable:
            return Err(f"[{self.name}] is not closable")
        elif self.is_closed:
            return Err(f"[{self.name}] is already closed")
        else:
            self.add_trait(Item.Trait.CLOSED)
            return Ok(Event.Closed(target=self.name))

    @staticmethod
    def from_json(data):
        name = data.get("name")
        description = data.get("description")
        traits = [Item.Trait(t) for t in data.get("traits", [])]
        assert name is not None
        return Item(name=name, description=description, traits=traits)

#------------------------------------------------------------------------------

class Items:
    def __init__(self, items):
        self._index = {item.name: item for item in items}

    def get(self, name):
        return self._index.get(name)

    def add(self, item):
        self._index[item.name] = item

    def names(self):
        return self._index.keys()

    @staticmethod
    def from_json(data):
        return Items(items=[Item.from_json(i) for i in data])

#------------------------------------------------------------------------------
