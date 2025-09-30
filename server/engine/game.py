import os
import json

from enum import Enum
from attrs import define, field
from cattrs import structure, unstructure

#------------------------------------------------------------------------------

class ItemTrait(Enum):
  TAKEABLE   = "takeable"      # can be taken by the player (inventory)
  OPENABLE   = "openable"      # can be opened
  CLOSABLE   = "closable"      # can be closed
  LOCKABLE   = "lockable"      # can be locked
  UNLOCKABLE = "unlockable"    # can be unlocked
  CONTAINER  = "container"     # holds items inside
  COMPOSITE  = "composite"     # is made up of parts
  SUPPORTER  = "supporter"     # items rest on top
  READABLE   = "readable"      # has text to read
  WEARABLE   = "wearable"      # can put on/take off
  EDIBLE     = "edible"        # can be consumed

#------------------------------------------------------------------------------

@define
class Item:
    name: str
    description: str
    traits: list[ItemTrait] = field(factory=list)

@define
class Room:
    name: str
    items: list[Item] = field(factory=list)

    def facts(self):
        return []


@define
class Game:
    rooms: list[Room] = field(factory=list)

    @staticmethod
    def load(filename):
        with open(filename) as f:
            return structure(json.load(f), Game)
