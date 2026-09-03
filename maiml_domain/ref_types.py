"""
MaiML Reference Types
Corresponds to: maiml-refTypes.xsd

All are concrete extensions of ReferenceObjectType.
"""

from __future__ import annotations
from typing import Optional
from .core import ReferenceObjectType


class CreatorRefType(ReferenceObjectType):
    """Reference to a creator element."""
    pass


class VendorRefType(ReferenceObjectType):
    """Reference to a vendor element."""
    pass


class OwnerRefType(ReferenceObjectType):
    """Reference to an owner element."""
    pass


class InstrumentRefType(ReferenceObjectType):
    """Reference to an instrument element."""
    pass


class PlaceRefType(ReferenceObjectType):
    """
    Reference to a PNML place element.
    Optional initialMarking attribute (xs:boolean).
    """
    def __init__(
        self,
        id: str,
        ref: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        initial_marking: Optional[bool] = None,
    ):
        super().__init__(id, ref, name, description)
        self.initial_marking: Optional[bool] = initial_marking


class TransitionRefType(ReferenceObjectType):
    """Reference to a PNML transition element."""
    pass


class ResultsRefType(ReferenceObjectType):
    """Reference to a results element."""
    pass


class TemplateRefType(ReferenceObjectType):
    """Reference to a template element (material/condition/result template)."""
    pass


class InstanceRefType(ReferenceObjectType):
    """Reference to an instance of a template."""
    pass


__all__ = [
    "CreatorRefType",
    "VendorRefType",
    "OwnerRefType",
    "InstrumentRefType",
    "PlaceRefType",
    "TransitionRefType",
    "ResultsRefType",
    "TemplateRefType",
    "InstanceRefType",
]
