import pytest
from .game import Game, Room, Item

#------------------------------------------------------------------------------

def test_game():

    game = Game.load("data/example.json")
    assert game is not None

    assert len(game.rooms) == 3
    [r1, r2, r3] = game.rooms

    assert r1.name == "The First Room"
    assert r2.name == "The Middle Room"
    assert r3.name == "The Final Room"

    assert r1.facts() == [
    ]

#------------------------------------------------------------------------------
