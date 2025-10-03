from enum import Enum

class Relationship:
    class Kind(Enum):
        HAS      = "has"
        CONTAINS = "contains"
        SUPPORTS = "supports"

    def __init__(self, kind, source, target):
        self.kind = kind
        self.source = source
        self.target = target

    @staticmethod
    def from_json(data):
        return Relationship(
            kind=Relationship.Kind(data.get("relationship") or data.get("kind")),
            source=data.get("source"),
            target=data.get("target")
        )

    @property
    def fact(self):
        return f"The [{self.source}] {self.kind.value} a [{self.target}]"

Relationships = list[Relationship]

#------------------------------------------------------------------------------
