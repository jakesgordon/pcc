import pytest
from .item import Item, Items
from .event import Event

THING="thing"

#------------------------------------------------------------------------------

def test_item_defaults():

    item = Item(THING)

    assert item.name         == THING
    assert item.description  == None

    assert item.is_takeable  == False
    assert item.is_openable  == False
    assert item.is_closable  == False
    assert item.is_container == False

    assert item.is_taken     == False
    assert item.is_open      == False
    assert item.is_closed    == False
    assert item.is_locked    == False

    result = item.take()
    assert result.err_value == "[thing] is not takeable"

    result = item.open()
    assert result.err_value == "[thing] is not openable"

    result = item.close()
    assert result.err_value == "[thing] is not closable"

#------------------------------------------------------------------------------

def test_takeable():

    item = Item(THING, traits=[Item.Trait.TAKEABLE])

    assert item.is_takeable == True
    assert item.is_taken    == False

    result = item.take()
    assert result.is_ok()
    assert result.ok_value  == Event.Taken(target=THING)
    assert item.is_taken    == True

    result = item.take()
    assert result.is_err()
    assert result.err_value == "[thing] has already been taken"

#------------------------------------------------------------------------------

def test_openable():

    item = Item(THING, traits=[Item.Trait.OPENABLE, Item.Trait.CLOSED])

    assert item.is_openable == True
    assert item.is_closable == False
    assert item.is_open     == False
    assert item.is_closed   == True

    result = item.open()
    assert result.is_ok()
    assert result.ok_value == Event.Opened(target=THING)
    assert item.is_open    == True
    assert item.is_closed  == False

    result = item.open()
    assert result.is_err()
    assert result.err_value == "[thing] is already open"

    result = item.close()
    assert result.is_err()
    assert result.err_value == "[thing] is not closable"

#------------------------------------------------------------------------------

def test_closable():

    item = Item(THING, traits=[Item.Trait.CLOSABLE])

    assert item.is_openable == False
    assert item.is_closable == True
    assert item.is_open     == True
    assert item.is_closed   == False

    result = item.close()
    assert result.is_ok()
    assert result.ok_value == Event.Closed(target=THING)
    assert item.is_open    == False
    assert item.is_closed  == True

    result = item.close()
    assert result.is_err()
    assert result.err_value == "[thing] is already closed"

    result = item.open()
    assert result.is_err()
    assert result.err_value == "[thing] is not openable"

#------------------------------------------------------------------------------

def test_openable_and_closeable():

    item = Item(THING, traits=[Item.Trait.OPENABLE, Item.Trait.CLOSABLE])

    assert item.is_openable == True
    assert item.is_closable == True
    assert item.is_open     == True
    assert item.is_closed   == False

    result = item.close()
    assert result.is_ok()
    assert result.ok_value == Event.Closed(target=THING)
    assert item.is_open    == False
    assert item.is_closed  == True

    result = item.open()
    assert result.is_ok()
    assert result.ok_value == Event.Opened(target=THING)
    assert item.is_open    == True
    assert item.is_closed  == False

#------------------------------------------------------------------------------

def test_container_combinations():

    container = Item(THING, traits=[Item.Trait.CONTAINER])
    assert container.is_openable == False
    assert container.is_closable == False
    assert container.is_open     == True
    assert container.is_closed   == False

    container = Item(THING, traits=[Item.Trait.CONTAINER, Item.Trait.CLOSABLE])
    assert container.is_openable == False
    assert container.is_closable == True
    assert container.is_open     == True
    assert container.is_closed   == False

    container = Item(THING, traits=[Item.Trait.CONTAINER, Item.Trait.CLOSABLE, Item.Trait.CLOSED])
    assert container.is_openable == False
    assert container.is_closable == True
    assert container.is_open     == False
    assert container.is_closed   == True

    container = Item(THING, traits=[Item.Trait.CONTAINER, Item.Trait.OPENABLE])
    assert container.is_openable == True
    assert container.is_closable == False
    assert container.is_open     == True
    assert container.is_closed   == False

    container = Item(THING, traits=[Item.Trait.CONTAINER, Item.Trait.OPENABLE, Item.Trait.CLOSED])
    assert container.is_openable == True
    assert container.is_closable == False
    assert container.is_open     == False
    assert container.is_closed   == True

    container = Item(THING, traits=[Item.Trait.CONTAINER, Item.Trait.OPENABLE, Item.Trait.CLOSABLE])
    assert container.is_openable == True
    assert container.is_closable == True
    assert container.is_open     == True
    assert container.is_closed   == False

    container = Item(THING, traits=[Item.Trait.CONTAINER, Item.Trait.OPENABLE, Item.Trait.CLOSABLE, Item.Trait.CLOSED])
    assert container.is_openable == True
    assert container.is_closable == True
    assert container.is_open     == False
    assert container.is_closed   == True

#------------------------------------------------------------------------------

def test_items():

    item1 = Item("first")
    item2 = Item("second")
    item3 = Item("third")
    item4 = Item("fourth")

    items = Items([item1, item2, item3])
    items.add(item4)

    assert items.get("first")  == item1
    assert items.get("second") == item2
    assert items.get("third")  == item3
    assert items.get("fourth") == item4

    assert sorted(items.names()) == sorted([
        "first",
        "second",
        "third",
        "fourth"
    ])

#------------------------------------------------------------------------------
