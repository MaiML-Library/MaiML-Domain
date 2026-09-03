"""
MaiML Root Object Types
Corresponds to: maiml.xsd (rootObjectType, maimlRootType, protocolFileRootType)

RootObjectType (abstract)
  ├── MaimlRootType        — full maiml file (document + protocol + data + eventLog)
  └── ProtocolFileRootType — protocol-only file (document + protocol)
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional

from .document import DocumentType
from .protocol import ProtocolType
from .data import DataType
from .event_log import EventLogType


class RootObjectType(ABC):
    """
    Abstract root of a MaiML file.
    version attribute is fixed to "1.0".
    Optional features attribute (space-separated feature tokens).
    """

    VERSION: str = "1.0"

    def __init__(
        self,
        document: DocumentType,
        features: Optional[str] = None,
    ):
        if not isinstance(document, DocumentType):
            raise TypeError("RootObjectType requires a DocumentType instance")
        self.document: DocumentType = document
        self.features: Optional[str] = features

    @property
    def version(self) -> str:
        return self.VERSION

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(version={self.version!r})"


class MaimlRootType(RootObjectType):
    """
    A complete MaiML document: document + protocol + data + eventLog.
    Corresponds to the <maiml> root element with all four sections.
    """

    def __init__(
        self,
        document: DocumentType,
        protocol: ProtocolType,
        data: DataType,
        event_log: EventLogType,
        features: Optional[str] = None,
    ):
        super().__init__(document, features)
        if not isinstance(protocol, ProtocolType):
            raise TypeError("MaimlRootType requires a ProtocolType instance")
        if not isinstance(data, DataType):
            raise TypeError("MaimlRootType requires a DataType instance")
        if not isinstance(event_log, EventLogType):
            raise TypeError("MaimlRootType requires an EventLogType instance")

        self.protocol: ProtocolType = protocol
        self.data: DataType = data
        self.event_log: EventLogType = event_log

    def __repr__(self) -> str:
        return (
            f"MaimlRootType(version={self.version!r}, "
            f"document={self.document!r})"
        )


class ProtocolFileRootType(RootObjectType):
    """
    A MaiML protocol-only file: document + protocol (no data / eventLog).
    Used when distributing measurement protocols separately.
    """

    def __init__(
        self,
        document: DocumentType,
        protocol: ProtocolType,
        features: Optional[str] = None,
    ):
        super().__init__(document, features)
        if not isinstance(protocol, ProtocolType):
            raise TypeError("ProtocolFileRootType requires a ProtocolType instance")
        self.protocol: ProtocolType = protocol

    def __repr__(self) -> str:
        return (
            f"ProtocolFileRootType(version={self.version!r}, "
            f"document={self.document!r})"
        )


__all__ = [
    "RootObjectType",
    "MaimlRootType",
    "ProtocolFileRootType",
]
