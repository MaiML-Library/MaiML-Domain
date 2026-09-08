"""
MaiML Document Types
Corresponds to: maiml-document.xsd

DocumentType is the root of the <document> section of every MaiML file.
"""

from __future__ import annotations
from datetime import datetime
from typing import List, Optional

from .core import HasIdAttributeType, GlobalObjectContent, HashType, _StrictAttributesMixin
from .simple_types import Uuid
from .ref_types import VendorRefType, InstrumentRefType


# ---------------------------------------------------------------------------
# ChainType  (recursive)
# ---------------------------------------------------------------------------

class ChainType(_StrictAttributesMixin):
    """
    Integrity chain: uuid + hash + optional nested chains.
    Optional 'key' attribute.
    """

    def __init__(
        self,
        uuid: Uuid,
        hash: HashType,
        chains: Optional[List["ChainType"]] = None,
        key: Optional[str] = None,
    ):
        self.uuid: Uuid = uuid
        self.hash: HashType = hash
        self.chains: List["ChainType"] = chains or []
        self.key: Optional[str] = key

    def __repr__(self) -> str:
        return f"ChainType(uuid={self.uuid!r}, key={self.key!r})"


# ---------------------------------------------------------------------------
# ParentType  (recursive)
# ---------------------------------------------------------------------------

class ParentType(_StrictAttributesMixin):
    """
    Parent document reference: uuid + hash + optional nested parents.
    Optional 'key' attribute.
    """

    def __init__(
        self,
        uuid: Uuid,
        hash: HashType,
        parents: Optional[List["ParentType"]] = None,
        key: Optional[str] = None,
    ):
        self.uuid: Uuid = uuid
        self.hash: HashType = hash
        self.parents: List["ParentType"] = parents or []
        self.key: Optional[str] = key

    def __repr__(self) -> str:
        return f"ParentType(uuid={self.uuid!r}, key={self.key!r})"


# ---------------------------------------------------------------------------
# VendorType
# ---------------------------------------------------------------------------

class VendorType(HasIdAttributeType):
    """
    Vendor entity within a document.
    Content: globalObjectContentGroup.
    """

    def __init__(self, id: str, content: Optional[GlobalObjectContent] = None):
        super().__init__(id)
        self.content: GlobalObjectContent = content or GlobalObjectContent()

    def __repr__(self) -> str:
        return f"VendorType(id={self.id!r})"


# ---------------------------------------------------------------------------
# OwnerType
# ---------------------------------------------------------------------------

class OwnerType(HasIdAttributeType):
    """
    Owner entity within a document.
    Content: globalObjectContentGroup.
    """

    def __init__(self, id: str, content: Optional[GlobalObjectContent] = None):
        super().__init__(id)
        self.content: GlobalObjectContent = content or GlobalObjectContent()

    def __repr__(self) -> str:
        return f"OwnerType(id={self.id!r})"


# ---------------------------------------------------------------------------
# InstrumentType
# ---------------------------------------------------------------------------

class InstrumentType(HasIdAttributeType):
    """
    Instrument entity within a document.
    Content: globalObjectContentGroup.
    """

    def __init__(self, id: str, content: Optional[GlobalObjectContent] = None):
        super().__init__(id)
        self.content: GlobalObjectContent = content or GlobalObjectContent()

    def __repr__(self) -> str:
        return f"InstrumentType(id={self.id!r})"


# ---------------------------------------------------------------------------
# CreatorType
# ---------------------------------------------------------------------------

class CreatorType(HasIdAttributeType):
    """
    Creator entity: a person/software that created (part of) the document.
    Requires 1+ VendorRefType; optional InstrumentRefType.
    Content: globalObjectContentGroup + refs.
    """

    def __init__(
        self,
        id: str,
        vendor_refs: Optional[List[VendorRefType]] = None,
        content: Optional[GlobalObjectContent] = None,
        instrument_refs: Optional[List[InstrumentRefType]] = None,
    ):
        super().__init__(id)
        if not vendor_refs:
            raise ValueError("CreatorType requires at least one VendorRefType")
        self.vendor_refs: List[VendorRefType] = vendor_refs
        self.content: GlobalObjectContent = content or GlobalObjectContent()
        self.instrument_refs: List[InstrumentRefType] = instrument_refs or []

    def __repr__(self) -> str:
        return f"CreatorType(id={self.id!r})"


# ---------------------------------------------------------------------------
# DocumentType
# ---------------------------------------------------------------------------

class DocumentType(HasIdAttributeType):
    """
    The <document> section of a MaiML file.

    Required:
      - id attribute
      - content (globalObjectContentGroup)
      - 1+ creator
      - 1+ vendor
      - 1+ owner
      - date (xs:dateTime)

    Optional:
      - XMLDSig Signature (not modelled here; store as raw str)
      - instrument (0+)
      - chain (0+)
      - parent (0+)
    """

    def __init__(
        self,
        id: str,
        date: datetime,
        creators: Optional[List[CreatorType]] = None,
        vendors: Optional[List[VendorType]] = None,
        owners: Optional[List[OwnerType]] = None,
        content: Optional[GlobalObjectContent] = None,
        instruments: Optional[List[InstrumentType]] = None,
        chains: Optional[List[ChainType]] = None,
        parents: Optional[List[ParentType]] = None,
        signature: Optional[str] = None,
    ):
        super().__init__(id)
        if not creators:
            raise ValueError("DocumentType requires at least one CreatorType")
        if not vendors:
            raise ValueError("DocumentType requires at least one VendorType")
        if not owners:
            raise ValueError("DocumentType requires at least one OwnerType")

        self.date: datetime = date
        self.creators: List[CreatorType] = creators
        self.vendors: List[VendorType] = vendors
        self.owners: List[OwnerType] = owners
        self.content: GlobalObjectContent = content or GlobalObjectContent()
        self.instruments: List[InstrumentType] = instruments or []
        self.chains: List[ChainType] = chains or []
        self.parents: List[ParentType] = parents or []
        self.signature: Optional[str] = signature   # raw XML string placeholder

    def __repr__(self) -> str:
        return (
            f"DocumentType(id={self.id!r}, date={self.date!r}, "
            f"creators={len(self.creators)}, vendors={len(self.vendors)})"
        )


__all__ = [
    "ChainType",
    "ParentType",
    "VendorType",
    "OwnerType",
    "InstrumentType",
    "CreatorType",
    "DocumentType",
]
