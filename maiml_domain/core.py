"""
MaiML Core Types
Corresponds to: maiml-core.xsd

Defines abstract base types and shared structural types used throughout MaiML.
"""

from __future__ import annotations
from abc import ABC
from dataclasses import dataclass, field
from typing import List, Optional
from .simple_types import Uuid


# ---------------------------------------------------------------------------
# HashType
# ---------------------------------------------------------------------------

@dataclass
class HashType:
    """
    Binary hash value with an optional hashing method attribute.
    xs:base64Binary content + method attribute.
    """
    value: bytes                     # base64-decoded bytes
    method: Optional[str] = None     # e.g. "SHA-256"

    def __post_init__(self):
        if not isinstance(self.value, (bytes, bytearray)):
            raise TypeError("HashType.value must be bytes")

    def __repr__(self) -> str:
        return f"HashType(method={self.method!r}, bytes={len(self.value)}B)"


# ---------------------------------------------------------------------------
# InsertionType  (external reference embedded in a global object)
# ---------------------------------------------------------------------------

@dataclass
class InsertionType:
    """
    Reference to an external resource by URI + hash, with optional UUID/format.
    """
    uri: str                         # xs:anyURI
    hash: HashType
    uuid: Optional[Uuid] = None
    format: Optional[str] = None

    def __post_init__(self):
        if not self.uri:
            raise ValueError("InsertionType.uri must not be empty")


# ---------------------------------------------------------------------------
# EncryptionType  (encryptionGroup: encrypted-content branch)
# ---------------------------------------------------------------------------

@dataclass
class EncryptionType:
    """
    Encrypted-content branch of globalObjectContentGroup, and of every
    property*/content* type's own xs:choice (encryptionGroup in
    maiml-property.xsd / maiml-core.xsd):

        childUri* + childHash* + childUuid* + xenc:EncryptedData (required)

    xenc:EncryptedData (XML Encryption Syntax) is not modelled structurally
    in this domain layer -- it is stored as the raw serialized
    <xenc:EncryptedData> XML string, the same treatment DocumentType gives
    ds:Signature. Actual encryption/decryption is out of scope for
    maiml_domain; SDKs built on top of this layer are expected to supply an
    XML-Encryption implementation.
    """
    encrypted_data: str                                      # raw <xenc:EncryptedData> XML (required)
    child_uris: List[str] = field(default_factory=list)       # xs:anyURI*
    child_hashes: List[bytes] = field(default_factory=list)   # xs:base64Binary*
    child_uuids: List[Uuid] = field(default_factory=list)     # uuid*

    def __post_init__(self) -> None:
        if not self.encrypted_data:
            raise ValueError("EncryptionType.encrypted_data must not be empty")

    def __repr__(self) -> str:
        return (
            f"EncryptionType(children={len(self.child_uris)}, "
            f"bytes={len(self.encrypted_data)})"
        )


# ---------------------------------------------------------------------------
# Abstract base: HasIdAttributeType
# ---------------------------------------------------------------------------

class HasIdAttributeType(ABC):
    """
    Abstract base for any element that carries a required xs:ID attribute.
    All major MaiML objects (document, protocol, data, …) inherit from this.
    """

    def __init__(self, id: str):
        if not id:
            raise ValueError("id must not be empty")
        self._id: str = id

    @property
    def id(self) -> str:
        return self._id

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self._id!r})"


# ---------------------------------------------------------------------------
# GlobalObjectContent mixin  (globalObjectContentGroup)
# ---------------------------------------------------------------------------

@dataclass
class GlobalObjectContent:
    """
    Mixin that provides the content carried by every 'global object':
      uuid, name, description, annotation, insertions, properties, contents
      -- OR, exclusively, an EncryptionType payload.

    Corresponds to globalObjectContentGroup in maiml-core.xsd +
    genericDataContainerGroup in maiml-property.xsd.

    globalObjectContentGroup is an xs:choice: after the uuid element, an
    object carries EITHER the plain fields below OR a single 'encryption'
    payload, never both. NOTE: the XSD marks 'uuid' required (no
    minOccurs="0"); it is kept Optional here so GlobalObjectContent()
    remains usable as a zero-arg default throughout this package -- callers
    that need strict XSD compliance should always supply one explicitly.
    """
    uuid: Optional[Uuid] = None
    name: Optional[str] = None           # xs:QName (stored as str)
    description: Optional[str] = None
    annotation: Optional[str] = None
    insertions: list = field(default_factory=list)   # list[InsertionType]
    properties: list = field(default_factory=list)   # list[PropertyBaseType]
    contents: list = field(default_factory=list)     # list[ContentBaseType]
    encryption: Optional[EncryptionType] = None

    def __post_init__(self) -> None:
        has_plain = (
            self.name is not None
            or self.description is not None
            or self.annotation is not None
            or bool(self.insertions)
            or bool(self.properties)
            or bool(self.contents)
        )
        if self.encryption is not None and has_plain:
            raise ValueError(
                "GlobalObjectContent: 'encryption' is mutually exclusive with "
                "insertions/name/description/annotation/properties/contents "
                "-- globalObjectContentGroup models this as an xs:choice."
            )


# ---------------------------------------------------------------------------
# Abstract base: SimpleObjectType
# ---------------------------------------------------------------------------

class SimpleObjectType(HasIdAttributeType):
    """
    Abstract base for objects with id + optional name/description.
    Used for pnml Place, Transition.
    """

    def __init__(
        self,
        id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ):
        super().__init__(id)
        self.name: Optional[str] = name
        self.description: Optional[str] = description


# ---------------------------------------------------------------------------
# Abstract base: ReferenceObjectType
# ---------------------------------------------------------------------------

class ReferenceObjectType(SimpleObjectType):
    """
    Abstract base for reference objects: SimpleObjectType + required ref (IDREF).
    """

    def __init__(
        self,
        id: str,
        ref: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ):
        super().__init__(id, name, description)
        if not ref:
            raise ValueError("ref must not be empty")
        self.ref: str = ref


# ---------------------------------------------------------------------------
# Abstract base: TripleObjectType
# ---------------------------------------------------------------------------

class TripleObjectType(SimpleObjectType):
    """
    Abstract base for arc-like objects: SimpleObjectType + source + target (IDREF).
    """

    def __init__(
        self,
        id: str,
        source: str,
        target: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ):
        super().__init__(id, name, description)
        if not source:
            raise ValueError("source must not be empty")
        if not target:
            raise ValueError("target must not be empty")
        self.source: str = source
        self.target: str = target


__all__ = [
    "HashType",
    "InsertionType",
    "EncryptionType",
    "HasIdAttributeType",
    "GlobalObjectContent",
    "SimpleObjectType",
    "ReferenceObjectType",
    "TripleObjectType",
]
