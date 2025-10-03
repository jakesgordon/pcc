import pytest
from .room import Room
from .command import Command
from .event import Event

#------------------------------------------------------------------------------

def test():

    room = Room.load("data/room1.json")
    assert room is not None
    assert room.name == "The First Room"
    assert room.events == []
    assert room.inventory == []

    assert room.facts() == [
        "The [room] can be described as 'a dusty study'",
        "The [room] has a [desk]",
        "The [room] has a [floor]",
        "The [room] has a [door]",
        "The [desk] can be described as 'a plain desk'",
        "The [desk] has a [drawer]",
        "The [drawer] can be described as 'a simple drawer'",
        "The [drawer] is closed",
        "The [floor] can be described as 'a plain wooden floor'",
        "The [door] can be described as 'a plain wooden door with a simple keyhole'",
        "The [door] is closed",
        "The [door] is locked",
    ]

    result = room.execute(Command.Open(target="drawer"))
    assert result.is_ok()
    assert result.ok_value == Event.Opened(target="drawer")

    assert room.facts() == [
        "The [room] can be described as 'a dusty study'",
        "The [room] has a [desk]",
        "The [room] has a [floor]",
        "The [room] has a [door]",
        "The [desk] can be described as 'a plain desk'",
        "The [desk] has a [drawer]",
        "The [drawer] can be described as 'a simple drawer'",
        "The [drawer] is open",
        "The [drawer] contains a [key]",
        "The [key] can be described as 'a gold key'",
        "The [floor] can be described as 'a plain wooden floor'",
        "The [door] can be described as 'a plain wooden door with a simple keyhole'",
        "The [door] is closed",
        "The [door] is locked",
    ]

    result = room.execute(Command.Take(target="key"))
    assert result.is_ok()
    assert result.ok_value == Event.Taken(target="key")

    # assert room.facts() == [
    #     "The [room] can be described as 'a dusty study'",
    #     "The [room] has a [desk]",
    #     "The [room] has a [floor]",
    #     "The [room] has a [door]",
    #     "The [desk] can be described as 'a plain desk'",
    #     "The [desk] has a [drawer]",
    #     "The [drawer] can be described as 'a simple drawer'",
    #     "The [drawer] is open",
    #     "The [drawer] is empty",
    #     "The [key] can be described as 'a gold key'",
    #     "The [floor] can be described as 'a plain wooden floor'",
    #     "The [door] can be described as 'a plain wooden door with a simple keyhole'",
    #     "The [door] is closed",
    #     "The [door] is locked",
    #     "The [player] has a [key]",
    #     "The [key] is a gold key",
    # ]

    # room.execute(Command.Unlock(target="door", using="key"))

    # assert room.facts() == [
    #     "The [room] contains a [desk]",
    #     "The [room] has a [floor]",
    #     "The [room] has a [door]",
    #     "The [desk] is a plain desk",
    #     "The [desk] has a [drawer]",
    #     "The [drawer] is a simple drawer",
    #     "The [drawer] is open",
    #     "The [drawer] is empty",
    #     "The [floor] is a plain wooden floor",
    #     "The [door] is a plain wooden door with a simple keyhole",
    #     "The [door] is closed",
    #     "The [door] is unlocked",
    #     "The [player] has a [key]",
    #     "The [key] is a gold key",
    # ]


    # room.execute(Command.Open(target="door"))

    assert room.events == [
        Event.Opened(target="drawer"),
        Event.Taken(target="key"),
    #   Event.Unlocked(target="door", using="key")
    ]

#------------------------------------------------------------------------------
