"""
MaiML PNML Types (Petri Net Markup Language subset)
Corresponds to: maiml-pnml.xsd
"""

from __future__ import annotations
from typing import List, Optional

from .core import HasIdAttributeType, GlobalObjectContent, SimpleObjectType, TripleObjectType


class PlaceType(SimpleObjectType):
    """
    A PNML place node.
    Extends SimpleObjectType: id + optional name/description.
    """
    def __repr__(self) -> str:
        return f"PlaceType(id={self.id!r}, name={self.name!r})"


class TransitionType(SimpleObjectType):
    """
    A PNML transition node.
    Extends SimpleObjectType: id + optional name/description.
    """
    def __repr__(self) -> str:
        return f"TransitionType(id={self.id!r}, name={self.name!r})"


class ArcType(TripleObjectType):
    """
    A PNML arc (directed edge from source to target).
    Extends TripleObjectType: id + source (IDREF) + target (IDREF) + optional name/description.
    """
    def __repr__(self) -> str:
        return f"ArcType(id={self.id!r}, source={self.source!r}, target={self.target!r})"


class PnmlType(HasIdAttributeType):
    """
    A Petri Net graph embedded in a MaiML method.

    Required:
      - id attribute
      - 1+ place
      - 1+ transition
      - 1+ arc

    Optional:
      - globalObjectContentGroup (uuid, name, description, annotation,
        insertions, properties, contents)
    """

    def __init__(
        self,
        id: str,
        places: Optional[List[PlaceType]] = None,
        transitions: Optional[List[TransitionType]] = None,
        arcs: Optional[List[ArcType]] = None,
        content: Optional[GlobalObjectContent] = None,
    ):
        super().__init__(id)
        if not places:
            raise ValueError("PnmlType requires at least one PlaceType")
        if not transitions:
            raise ValueError("PnmlType requires at least one TransitionType")
        if not arcs:
            raise ValueError("PnmlType requires at least one ArcType")

        self.places: List[PlaceType] = places
        self.transitions: List[TransitionType] = transitions
        self.arcs: List[ArcType] = arcs
        self.content: GlobalObjectContent = content or GlobalObjectContent()

    def __repr__(self) -> str:
        return (
            f"PnmlType(id={self.id!r}, places={len(self.places)}, "
            f"transitions={len(self.transitions)}, arcs={len(self.arcs)})"
        )


__all__ = [
    "PlaceType",
    "TransitionType",
    "ArcType",
    "PnmlType",
]
