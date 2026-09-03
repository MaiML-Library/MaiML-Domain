"""
MaiML Protocol Types
Corresponds to: maiml-protocol.xsd

Hierarchy:
  ProtocolType
    └── MethodType
          ├── PnmlType (1+)
          ├── ProgramType (1+)
          │     └── InstructionType (1+)
          ├── MaterialTemplateType (0+)
          ├── ConditionTemplateType (0+)
          └── ResultTemplateType (0+)
"""

from __future__ import annotations
from typing import List, Optional

from .core import HasIdAttributeType, GlobalObjectContent
from .pnml import PnmlType
from .ref_types import PlaceRefType, TransitionRefType, TemplateRefType


# ---------------------------------------------------------------------------
# InstructionType
# ---------------------------------------------------------------------------

class InstructionType(HasIdAttributeType):
    """
    A single instruction within a program.
    Refers to one or more PNML transitions.
    """

    def __init__(
        self,
        id: str,
        transition_refs: Optional[List[TransitionRefType]] = None,
        content: Optional[GlobalObjectContent] = None,
    ):
        super().__init__(id)
        if not transition_refs:
            raise ValueError("InstructionType requires at least one TransitionRefType")
        self.transition_refs: List[TransitionRefType] = transition_refs
        self.content: GlobalObjectContent = content or GlobalObjectContent()

    def __repr__(self) -> str:
        return f"InstructionType(id={self.id!r})"


# ---------------------------------------------------------------------------
# Template types (shared structure)
# ---------------------------------------------------------------------------

class _TemplateBase(HasIdAttributeType):
    """Common base for material/condition/result template types."""

    def __init__(
        self,
        id: str,
        place_refs: Optional[List[PlaceRefType]] = None,
        content: Optional[GlobalObjectContent] = None,
        template_refs: Optional[List[TemplateRefType]] = None,
    ):
        super().__init__(id)
        if not place_refs:
            raise ValueError(f"{self.__class__.__name__} requires at least one PlaceRefType")
        self.place_refs: List[PlaceRefType] = place_refs
        self.content: GlobalObjectContent = content or GlobalObjectContent()
        self.template_refs: List[TemplateRefType] = template_refs or []


class MaterialTemplateType(_TemplateBase):
    """Template defining material inputs for a method/program."""
    def __repr__(self) -> str:
        return f"MaterialTemplateType(id={self.id!r})"


class ConditionTemplateType(_TemplateBase):
    """Template defining condition parameters for a method/program."""
    def __repr__(self) -> str:
        return f"ConditionTemplateType(id={self.id!r})"


class ResultTemplateType(_TemplateBase):
    """Template defining result outputs for a method/program."""
    def __repr__(self) -> str:
        return f"ResultTemplateType(id={self.id!r})"


# ---------------------------------------------------------------------------
# ProgramType
# ---------------------------------------------------------------------------

class ProgramType(HasIdAttributeType):
    """
    A program within a method: sequence of instructions +
    optional material/condition/result templates.
    """

    def __init__(
        self,
        id: str,
        instructions: Optional[List[InstructionType]] = None,
        content: Optional[GlobalObjectContent] = None,
        material_templates: Optional[List[MaterialTemplateType]] = None,
        condition_templates: Optional[List[ConditionTemplateType]] = None,
        result_templates: Optional[List[ResultTemplateType]] = None,
    ):
        super().__init__(id)
        if not instructions:
            raise ValueError("ProgramType requires at least one InstructionType")
        self.instructions: List[InstructionType] = instructions
        self.content: GlobalObjectContent = content or GlobalObjectContent()
        self.material_templates: List[MaterialTemplateType] = material_templates or []
        self.condition_templates: List[ConditionTemplateType] = condition_templates or []
        self.result_templates: List[ResultTemplateType] = result_templates or []

    def __repr__(self) -> str:
        return f"ProgramType(id={self.id!r}, instructions={len(self.instructions)})"


# ---------------------------------------------------------------------------
# MethodType
# ---------------------------------------------------------------------------

class MethodType(HasIdAttributeType):
    """
    An analytical method: 1+ PNML graphs + 1+ programs +
    optional template definitions.
    """

    def __init__(
        self,
        id: str,
        pnmls: Optional[List[PnmlType]] = None,
        programs: Optional[List[ProgramType]] = None,
        content: Optional[GlobalObjectContent] = None,
        material_templates: Optional[List[MaterialTemplateType]] = None,
        condition_templates: Optional[List[ConditionTemplateType]] = None,
        result_templates: Optional[List[ResultTemplateType]] = None,
    ):
        super().__init__(id)
        if not pnmls:
            raise ValueError("MethodType requires at least one PnmlType")
        if not programs:
            raise ValueError("MethodType requires at least one ProgramType")
        self.pnmls: List[PnmlType] = pnmls
        self.programs: List[ProgramType] = programs
        self.content: GlobalObjectContent = content or GlobalObjectContent()
        self.material_templates: List[MaterialTemplateType] = material_templates or []
        self.condition_templates: List[ConditionTemplateType] = condition_templates or []
        self.result_templates: List[ResultTemplateType] = result_templates or []

    def __repr__(self) -> str:
        return (
            f"MethodType(id={self.id!r}, pnmls={len(self.pnmls)}, "
            f"programs={len(self.programs)})"
        )


# ---------------------------------------------------------------------------
# ProtocolType
# ---------------------------------------------------------------------------

class ProtocolType(HasIdAttributeType):
    """
    The <protocol> section of a MaiML file.
    Contains 1+ methods and optional template definitions shared across methods.
    """

    def __init__(
        self,
        id: str,
        methods: Optional[List[MethodType]] = None,
        content: Optional[GlobalObjectContent] = None,
        material_templates: Optional[List[MaterialTemplateType]] = None,
        condition_templates: Optional[List[ConditionTemplateType]] = None,
        result_templates: Optional[List[ResultTemplateType]] = None,
    ):
        super().__init__(id)
        if not methods:
            raise ValueError("ProtocolType requires at least one MethodType")
        self.methods: List[MethodType] = methods
        self.content: GlobalObjectContent = content or GlobalObjectContent()
        self.material_templates: List[MaterialTemplateType] = material_templates or []
        self.condition_templates: List[ConditionTemplateType] = condition_templates or []
        self.result_templates: List[ResultTemplateType] = result_templates or []

    def __repr__(self) -> str:
        return f"ProtocolType(id={self.id!r}, methods={len(self.methods)})"


__all__ = [
    "InstructionType",
    "MaterialTemplateType",
    "ConditionTemplateType",
    "ResultTemplateType",
    "ProgramType",
    "MethodType",
    "ProtocolType",
]
