"""
MaiML EventLog Types
Corresponds to: maiml-eventLog.xsd

Hierarchy:
  EventLogType
    └── LogType (1+)
          ├── ExtensionType (0+)
          ├── GlobalsType (0+)
          ├── ClassifierType (0+)
          └── TraceType (1+)
                └── EventType (1+)
"""

from __future__ import annotations
from abc import ABC
from typing import List, Optional

from .core import HasIdAttributeType, GlobalObjectContent, _StrictAttributesMixin
from .property import PropertyBaseType
from .ref_types import CreatorRefType, OwnerRefType, ResultsRefType


# ---------------------------------------------------------------------------
# AttributableType  (abstract)
# ---------------------------------------------------------------------------

class AttributableType(_StrictAttributesMixin, ABC):
    """
    Abstract base that carries a list of propertyBaseType elements.
    Used by GlobalsType.
    """

    def __init__(self, properties: Optional[List[PropertyBaseType]] = None):
        self.properties: List[PropertyBaseType] = properties or []


# ---------------------------------------------------------------------------
# ExtensionType
# ---------------------------------------------------------------------------

class ExtensionType(_StrictAttributesMixin):
    """
    XES extension declaration: name + prefix + uri (all required).
    """

    def __init__(self, name: str, prefix: str, uri: str):
        if not name:
            raise ValueError("ExtensionType.name must not be empty")
        if not prefix:
            raise ValueError("ExtensionType.prefix must not be empty")
        if not uri:
            raise ValueError("ExtensionType.uri must not be empty")
        self.name: str = name
        self.prefix: str = prefix
        self.uri: str = uri

    def __repr__(self) -> str:
        return f"ExtensionType(name={self.name!r}, prefix={self.prefix!r})"


# ---------------------------------------------------------------------------
# GlobalsType
# ---------------------------------------------------------------------------

class GlobalsType(AttributableType):
    """
    XES global defaults: scope attribute (required) + properties.
    """

    def __init__(self, scope: str, properties: Optional[List[PropertyBaseType]] = None):
        super().__init__(properties)
        if not scope:
            raise ValueError("GlobalsType.scope must not be empty")
        self.scope: str = scope

    def __repr__(self) -> str:
        return f"GlobalsType(scope={self.scope!r})"


# ---------------------------------------------------------------------------
# ClassifierType
# ---------------------------------------------------------------------------

class ClassifierType(_StrictAttributesMixin):
    """
    XES classifier: name + scope + keys (all required).
    """

    def __init__(self, name: str, scope: str, keys: str):
        if not name:
            raise ValueError("ClassifierType.name must not be empty")
        if not scope:
            raise ValueError("ClassifierType.scope must not be empty")
        if not keys:
            raise ValueError("ClassifierType.keys must not be empty")
        self.name: str = name
        self.scope: str = scope
        self.keys: str = keys    # xs:token (space-separated key names)

    def __repr__(self) -> str:
        return f"ClassifierType(name={self.name!r}, scope={self.scope!r})"


# ---------------------------------------------------------------------------
# EventType
# ---------------------------------------------------------------------------

class EventType(HasIdAttributeType):
    """
    A single event within a trace.
    ref (IDREF): required — points to an instruction or program.
    Optional results refs, creator refs, owner refs.
    """

    def __init__(
        self,
        id: str,
        ref: str,
        content: Optional[GlobalObjectContent] = None,
        results_refs: Optional[List[ResultsRefType]] = None,
        creator_refs: Optional[List[CreatorRefType]] = None,
        owner_refs: Optional[List[OwnerRefType]] = None,
    ):
        super().__init__(id)
        if not ref:
            raise ValueError("EventType.ref must not be empty")
        self.ref: str = ref
        self.content: GlobalObjectContent = content or GlobalObjectContent()
        self.results_refs: List[ResultsRefType] = results_refs or []
        self.creator_refs: List[CreatorRefType] = creator_refs or []
        self.owner_refs: List[OwnerRefType] = owner_refs or []

    def __repr__(self) -> str:
        return f"EventType(id={self.id!r}, ref={self.ref!r})"


# ---------------------------------------------------------------------------
# TraceType
# ---------------------------------------------------------------------------

class TraceType(HasIdAttributeType):
    """
    A trace (sequence of events) within a log.
    ref (IDREF): required — points to a method or program.
    """

    def __init__(
        self,
        id: str,
        ref: str,
        events: Optional[List[EventType]] = None,
        content: Optional[GlobalObjectContent] = None,
        creator_refs: Optional[List[CreatorRefType]] = None,
        owner_refs: Optional[List[OwnerRefType]] = None,
    ):
        super().__init__(id)
        if not ref:
            raise ValueError("TraceType.ref must not be empty")
        if not events:
            raise ValueError("TraceType requires at least one EventType")
        self.ref: str = ref
        self.events: List[EventType] = events
        self.content: GlobalObjectContent = content or GlobalObjectContent()
        self.creator_refs: List[CreatorRefType] = creator_refs or []
        self.owner_refs: List[OwnerRefType] = owner_refs or []

    def __repr__(self) -> str:
        return f"TraceType(id={self.id!r}, ref={self.ref!r}, events={len(self.events)})"


# ---------------------------------------------------------------------------
# LogType
# ---------------------------------------------------------------------------

class LogType(HasIdAttributeType):
    """
    A log within the eventLog section.
    ref (IDREF): required — points to a method.
    Contains 1+ traces, optional extensions, globals, classifiers.
    """

    def __init__(
        self,
        id: str,
        ref: str,
        traces: Optional[List[TraceType]] = None,
        content: Optional[GlobalObjectContent] = None,
        extensions: Optional[List[ExtensionType]] = None,
        globals: Optional[List[GlobalsType]] = None,
        classifiers: Optional[List[ClassifierType]] = None,
        creator_refs: Optional[List[CreatorRefType]] = None,
        owner_refs: Optional[List[OwnerRefType]] = None,
    ):
        super().__init__(id)
        if not ref:
            raise ValueError("LogType.ref must not be empty")
        if not traces:
            raise ValueError("LogType requires at least one TraceType")
        self.ref: str = ref
        self.traces: List[TraceType] = traces
        self.content: GlobalObjectContent = content or GlobalObjectContent()
        self.extensions: List[ExtensionType] = extensions or []
        self.globals: List[GlobalsType] = globals or []
        self.classifiers: List[ClassifierType] = classifiers or []
        self.creator_refs: List[CreatorRefType] = creator_refs or []
        self.owner_refs: List[OwnerRefType] = owner_refs or []

    def __repr__(self) -> str:
        return f"LogType(id={self.id!r}, ref={self.ref!r}, traces={len(self.traces)})"


# ---------------------------------------------------------------------------
# EventLogType
# ---------------------------------------------------------------------------

class EventLogType(HasIdAttributeType):
    """
    The <eventLog> section of a MaiML file.
    Contains 1+ log objects.
    """

    def __init__(
        self,
        id: str,
        logs: Optional[List[LogType]] = None,
        content: Optional[GlobalObjectContent] = None,
    ):
        super().__init__(id)
        if not logs:
            raise ValueError("EventLogType requires at least one LogType")
        self.logs: List[LogType] = logs
        self.content: GlobalObjectContent = content or GlobalObjectContent()

    def __repr__(self) -> str:
        return f"EventLogType(id={self.id!r}, logs={len(self.logs)})"


__all__ = [
    "AttributableType",
    "ExtensionType",
    "GlobalsType",
    "ClassifierType",
    "EventType",
    "TraceType",
    "LogType",
    "EventLogType",
]
