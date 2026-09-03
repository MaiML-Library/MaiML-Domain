"""
MaiML Data Types
Corresponds to: maiml-data.xsd

The <data> section holds measurement results, organized as:
  DataType
    └── ResultsType (1+)
          ├── MaterialType (0+)   — references a materialTemplate
          ├── ConditionType (0+)  — references a conditionTemplate
          └── ResultType (0+)     — references a resultTemplate
"""

from __future__ import annotations
from typing import List, Optional

from .core import HasIdAttributeType, GlobalObjectContent
from .ref_types import InstanceRefType


# ---------------------------------------------------------------------------
# MaterialType
# ---------------------------------------------------------------------------

class MaterialType(HasIdAttributeType):
    """
    Measured material record. References a materialTemplate (ref attribute).
    May include instance references for sub-items.
    """

    def __init__(
        self,
        id: str,
        ref: str,
        content: Optional[GlobalObjectContent] = None,
        instance_refs: Optional[List[InstanceRefType]] = None,
    ):
        super().__init__(id)
        if not ref:
            raise ValueError("MaterialType.ref must not be empty")
        self.ref: str = ref
        self.content: GlobalObjectContent = content or GlobalObjectContent()
        self.instance_refs: List[InstanceRefType] = instance_refs or []

    def __repr__(self) -> str:
        return f"MaterialType(id={self.id!r}, ref={self.ref!r})"


# ---------------------------------------------------------------------------
# ConditionType
# ---------------------------------------------------------------------------

class ConditionType(HasIdAttributeType):
    """
    Measurement condition record. References a conditionTemplate (ref attribute).
    """

    def __init__(
        self,
        id: str,
        ref: str,
        content: Optional[GlobalObjectContent] = None,
        instance_refs: Optional[List[InstanceRefType]] = None,
    ):
        super().__init__(id)
        if not ref:
            raise ValueError("ConditionType.ref must not be empty")
        self.ref: str = ref
        self.content: GlobalObjectContent = content or GlobalObjectContent()
        self.instance_refs: List[InstanceRefType] = instance_refs or []

    def __repr__(self) -> str:
        return f"ConditionType(id={self.id!r}, ref={self.ref!r})"


# ---------------------------------------------------------------------------
# ResultType
# ---------------------------------------------------------------------------

class ResultType(HasIdAttributeType):
    """
    Measurement result record. References a resultTemplate (ref attribute).
    """

    def __init__(
        self,
        id: str,
        ref: str,
        content: Optional[GlobalObjectContent] = None,
        instance_refs: Optional[List[InstanceRefType]] = None,
    ):
        super().__init__(id)
        if not ref:
            raise ValueError("ResultType.ref must not be empty")
        self.ref: str = ref
        self.content: GlobalObjectContent = content or GlobalObjectContent()
        self.instance_refs: List[InstanceRefType] = instance_refs or []

    def __repr__(self) -> str:
        return f"ResultType(id={self.id!r}, ref={self.ref!r})"


# ---------------------------------------------------------------------------
# ResultsType
# ---------------------------------------------------------------------------

class ResultsType(HasIdAttributeType):
    """
    A set of measurement results for one experimental run.
    Contains optional materials, conditions, and result records.
    """

    def __init__(
        self,
        id: str,
        content: Optional[GlobalObjectContent] = None,
        materials: Optional[List[MaterialType]] = None,
        conditions: Optional[List[ConditionType]] = None,
        results: Optional[List[ResultType]] = None,
    ):
        super().__init__(id)
        self.content: GlobalObjectContent = content or GlobalObjectContent()
        self.materials: List[MaterialType] = materials or []
        self.conditions: List[ConditionType] = conditions or []
        self.results: List[ResultType] = results or []

    def __repr__(self) -> str:
        return (
            f"ResultsType(id={self.id!r}, materials={len(self.materials)}, "
            f"conditions={len(self.conditions)}, results={len(self.results)})"
        )


# ---------------------------------------------------------------------------
# DataType
# ---------------------------------------------------------------------------

class DataType(HasIdAttributeType):
    """
    The <data> section of a MaiML file.
    Contains 1+ ResultsType objects.
    """

    def __init__(
        self,
        id: str,
        results_list: Optional[List[ResultsType]] = None,
        content: Optional[GlobalObjectContent] = None,
    ):
        super().__init__(id)
        if not results_list:
            raise ValueError("DataType requires at least one ResultsType")
        self.results_list: List[ResultsType] = results_list
        self.content: GlobalObjectContent = content or GlobalObjectContent()

    def __repr__(self) -> str:
        return f"DataType(id={self.id!r}, results_count={len(self.results_list)})"


__all__ = [
    "MaterialType",
    "ConditionType",
    "ResultType",
    "ResultsType",
    "DataType",
]
