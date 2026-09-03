"""
MaiML Property & Content Types
Corresponds to: maiml-property.xsd

Hierarchy:
  UncertaintyBaseType (abstract)
    ├── PropertyBaseType (abstract)   → all property*Type classes
    └── ContentBaseType (abstract)    → all content*Type classes

Every concrete property*/content* type's own XSD definition offers an
xs:choice between plain content (value/description/uncertainty/generic data
container) and encryptionGroup (a fully-encrypted payload). That choice is
centralized once here via the 'encryption' field on UncertaintyBaseType
instead of being repeated on each of the ~50 leaf classes; see
core.EncryptionType for the encrypted-payload shape.
"""

from __future__ import annotations
from abc import ABC
from datetime import datetime
from decimal import Decimal
from typing import Any, List, Optional

from .core import EncryptionType


# ---------------------------------------------------------------------------
# Abstract bases
# ---------------------------------------------------------------------------

class UncertaintyBaseType(ABC):
    """
    Root abstract type for both property and content.
    Carries a required 'key' attribute (xs:QName stored as str) and the
    optional EncryptionType payload shared by every property*/content* type.
    """
    def __init__(self, key: str, encryption: Optional[EncryptionType] = None):
        if not key:
            raise ValueError("key must not be empty")
        self.key: str = key
        self.encryption: Optional[EncryptionType] = encryption

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(key={self.key!r})"


class PropertyBaseType(UncertaintyBaseType, ABC):
    """Abstract base for all property types."""
    pass


class ContentBaseType(UncertaintyBaseType, ABC):
    """
    Abstract base for all content types.
    Adds axis, size, id, ref attributes (all optional).
    """
    def __init__(
        self,
        key: str,
        axis: Optional[str] = None,
        size: Optional[int] = None,
        id: Optional[str] = None,
        ref: Optional[str] = None,
        encryption: Optional[EncryptionType] = None,
    ):
        super().__init__(key, encryption=encryption)
        self.axis = axis
        self.size = size
        self.id = id
        self.ref = ref


# ---------------------------------------------------------------------------
# Property: scalar types
# ---------------------------------------------------------------------------

class _ScalarPropertyBase(PropertyBaseType):
    """
    Shared base for property scalar types with no formatString/units/
    scaleFactor attributes (string, token, id, idRef, qualifiedName,
    boolean, base64Binary, hexBinary, uri, uuid, language).
    """
    def __init__(self, key: str, value: Any = None,
                 description: Optional[str] = None,
                 uncertainties: Optional[list] = None,
                 properties: Optional[list] = None,
                 contents: Optional[list] = None,
                 encryption: Optional[EncryptionType] = None):
        super().__init__(key, encryption=encryption)
        self.value = value
        self.description = description
        self.uncertainties: list = uncertainties or []
        self.properties: list = properties or []
        self.contents: list = contents or []
        if encryption is not None and (
            value is not None or description is not None
            or self.uncertainties or self.properties or self.contents
        ):
            raise ValueError(
                f"{self.__class__.__name__}: 'encryption' cannot be combined "
                "with value/description/uncertainty/property/content -- "
                "this type's XSD definition models the two as an xs:choice."
            )

    def __repr__(self):
        return f"{self.__class__.__name__}(key={self.key!r}, value={self.value!r})"


class StringType(_ScalarPropertyBase):
    """Property: xs:string scalar."""

class TokenType(_ScalarPropertyBase):
    """Property: xs:token scalar."""

class IdType(_ScalarPropertyBase):
    """Property: xs:ID scalar (nillable)."""

class IdRefType(_ScalarPropertyBase):
    """Property: xs:IDREF scalar (nillable)."""

class QualifiedNameType(_ScalarPropertyBase):
    """Property: xs:QName scalar (nillable)."""


class DateTimeType(_ScalarPropertyBase):
    """Property: xs:dateTime scalar (nillable). Optional formatString attribute."""
    def __init__(self, key: str, value: Optional[datetime] = None,
                 description: Optional[str] = None,
                 uncertainties: Optional[list] = None,
                 properties: Optional[list] = None,
                 contents: Optional[list] = None,
                 encryption: Optional[EncryptionType] = None,
                 format_string: Optional[str] = None):
        super().__init__(key, value, description, uncertainties, properties,
                          contents, encryption)
        self.format_string = format_string


class _NumericScalarPropertyBase(_ScalarPropertyBase):
    """
    Shared base for numeric property scalar types with optional
    formatString/units/scaleFactor attributes (decimal, double, float, int,
    long, short, byte, unsignedInt, unsignedLong, unsignedShort,
    unsignedByte). These three attributes sit outside the XSD's xs:choice,
    so they are allowed regardless of 'encryption'.
    """
    def __init__(self, key: str, value: Any = None,
                 description: Optional[str] = None,
                 uncertainties: Optional[list] = None,
                 properties: Optional[list] = None,
                 contents: Optional[list] = None,
                 encryption: Optional[EncryptionType] = None,
                 format_string: Optional[str] = None,
                 units: Optional[str] = None,
                 scale_factor: Optional[float] = None):
        super().__init__(key, value, description, uncertainties, properties,
                          contents, encryption)
        self.format_string = format_string
        self.units = units
        self.scale_factor = scale_factor


class DecimalType(_NumericScalarPropertyBase):
    """Property: xs:decimal scalar. Optional formatString, units, scaleFactor."""

class DoubleType(_NumericScalarPropertyBase):
    """Property: xs:double scalar. Optional formatString, units, scaleFactor."""

class FloatType(_NumericScalarPropertyBase):
    """Property: xs:float scalar. Optional formatString, units, scaleFactor."""

class IntType(_NumericScalarPropertyBase):
    """Property: xs:int scalar. Optional formatString, units, scaleFactor."""

class LongType(_NumericScalarPropertyBase):
    """Property: xs:long scalar."""

class ShortType(_NumericScalarPropertyBase):
    """Property: xs:short scalar."""

class ByteType(_NumericScalarPropertyBase):
    """Property: xs:byte scalar."""

class UnsignedIntType(_NumericScalarPropertyBase):
    """Property: xs:unsignedInt scalar."""

class UnsignedLongType(_NumericScalarPropertyBase):
    """Property: xs:unsignedLong scalar."""

class UnsignedShortType(_NumericScalarPropertyBase):
    """Property: xs:unsignedShort scalar."""

class UnsignedByteType(_NumericScalarPropertyBase):
    """Property: xs:unsignedByte scalar."""


class BooleanType(_ScalarPropertyBase):
    """Property: xs:boolean scalar."""

class Base64BinaryType(_ScalarPropertyBase):
    """Property: xs:base64Binary scalar."""

class HexBinaryType(_ScalarPropertyBase):
    """Property: xs:hexBinary scalar."""

class UriType(_ScalarPropertyBase):
    """Property: xs:anyURI scalar."""

class UuidType(_ScalarPropertyBase):
    """Property: MaiML uuid scalar (nillable)."""

class LanguageType(_ScalarPropertyBase):
    """Property: xs:language scalar (nillable)."""


# ---------------------------------------------------------------------------
# Property: list types
# ---------------------------------------------------------------------------

class _PropertyListBase(PropertyBaseType):
    """Shared base for property list types."""
    def __init__(self, key: str, values: Optional[List[Any]] = None,
                 description: Optional[str] = None,
                 uncertainties: Optional[list] = None,
                 properties: Optional[list] = None,
                 contents: Optional[list] = None,
                 encryption: Optional[EncryptionType] = None):
        super().__init__(key, encryption=encryption)
        self.values: List[Any] = values or []
        self.description = description
        self.uncertainties: list = uncertainties or []
        self.properties: list = properties or []
        self.contents: list = contents or []
        if encryption is not None and (
            self.values or description is not None
            or self.uncertainties or self.properties or self.contents
        ):
            raise ValueError(
                f"{self.__class__.__name__}: 'encryption' cannot be combined "
                "with values/description/uncertainty/property/content -- "
                "this type's XSD definition models the two as an xs:choice."
            )

    def __repr__(self):
        return f"{self.__class__.__name__}(key={self.key!r}, values={self.values!r})"


class PropertyListType(_PropertyListBase):
    """Property container (no direct value, only nested properties/contents)."""
    def __init__(self, key: str, description: Optional[str] = None,
                 uncertainties: Optional[list] = None,
                 properties: Optional[list] = None,
                 contents: Optional[list] = None,
                 encryption: Optional[EncryptionType] = None):
        # PropertyListType has no 'values'; reuse base with empty values
        super().__init__(key, [], description, uncertainties, properties,
                          contents, encryption)


class StringListType(_PropertyListBase):
    """Property: list of xs:string space-separated tokens."""

class IdRefListType(_PropertyListBase):
    """Property: list of xs:IDREF."""

class QualifiedNameListType(_PropertyListBase):
    """Property: list of xs:QName."""


class DateTimeListType(_PropertyListBase):
    """Property: list of xs:dateTime. Optional formatString."""
    def __init__(self, key: str, values: Optional[list] = None,
                 description: Optional[str] = None,
                 uncertainties: Optional[list] = None,
                 properties: Optional[list] = None,
                 contents: Optional[list] = None,
                 encryption: Optional[EncryptionType] = None,
                 format_string: Optional[str] = None):
        super().__init__(key, values, description, uncertainties, properties,
                          contents, encryption)
        self.format_string = format_string


class _NumericListProperty(_PropertyListBase):
    """Base for numeric list properties with units/scaleFactor."""
    def __init__(self, key: str, values: Optional[list] = None,
                 description: Optional[str] = None,
                 uncertainties: Optional[list] = None,
                 properties: Optional[list] = None,
                 contents: Optional[list] = None,
                 encryption: Optional[EncryptionType] = None,
                 format_string: Optional[str] = None,
                 units: Optional[str] = None,
                 scale_factor: Optional[float] = None):
        super().__init__(key, values, description, uncertainties, properties,
                          contents, encryption)
        self.format_string = format_string
        self.units = units
        self.scale_factor = scale_factor


class DecimalListType(_NumericListProperty):
    """Property: list of xs:decimal."""

class DoubleListType(_NumericListProperty):
    """Property: list of xs:double."""

class FloatListType(_NumericListProperty):
    """Property: list of xs:float."""

class IntListType(_NumericListProperty):
    """Property: list of xs:int."""

class LongListType(_NumericListProperty):
    """Property: list of xs:long."""

class ShortListType(_NumericListProperty):
    """Property: list of xs:short."""

class ByteListType(_NumericListProperty):
    """Property: list of xs:byte."""

class UnsignedIntListType(_NumericListProperty):
    """Property: list of xs:unsignedInt."""

class UnsignedLongListType(_NumericListProperty):
    """Property: list of xs:unsignedLong."""

class UnsignedShortListType(_NumericListProperty):
    """Property: list of xs:unsignedShort."""

class UnsignedByteListType(_NumericListProperty):
    """Property: list of xs:unsignedByte."""


class BooleanListType(_PropertyListBase):
    """Property: list of xs:boolean."""

class Base64BinaryListType(_PropertyListBase):
    """Property: list of xs:base64Binary."""

class HexBinaryListType(_PropertyListBase):
    """Property: list of xs:hexBinary."""

class UriListType(_PropertyListBase):
    """Property: list of xs:anyURI."""

class UuidListType(_PropertyListBase):
    """Property: list of MaiML uuid."""

class LanguageListType(_PropertyListBase):
    """Property: list of xs:language."""

class StringEnumType(_PropertyListBase):
    """Property: enumeration of xs:string values."""


# ---------------------------------------------------------------------------
# Content: list types  (axis, size, id, ref  + values)
# ---------------------------------------------------------------------------

class _ContentListBase(ContentBaseType):
    """Shared base for content list types."""
    def __init__(self, key: str, values: Optional[List[Any]] = None,
                 description: Optional[str] = None,
                 uncertainties: Optional[list] = None,
                 properties: Optional[list] = None,
                 contents: Optional[list] = None,
                 axis: Optional[str] = None,
                 size: Optional[int] = None,
                 id: Optional[str] = None,
                 ref: Optional[str] = None,
                 encryption: Optional[EncryptionType] = None):
        super().__init__(key, axis, size, id, ref, encryption)
        self.values: List[Any] = values or []
        self.description = description
        self.uncertainties: list = uncertainties or []
        self.properties: list = properties or []
        self.contents: list = contents or []
        if encryption is not None and (
            self.values or description is not None
            or self.uncertainties or self.properties or self.contents
        ):
            raise ValueError(
                f"{self.__class__.__name__}: 'encryption' cannot be combined "
                "with values/description/uncertainty/property/content -- "
                "this type's XSD definition models the two as an xs:choice."
            )

    def __repr__(self):
        return f"{self.__class__.__name__}(key={self.key!r}, values={self.values!r})"


class ContentStringListType(_ContentListBase):
    """Content: list of xs:string."""

class ContentIdRefListType(_ContentListBase):
    """Content: list of xs:IDREF."""

class ContentQualifiedNameListType(_ContentListBase):
    """Content: list of xs:QName."""


class ContentDateTimeListType(_ContentListBase):
    """Content: list of xs:dateTime. Optional formatString."""
    def __init__(self, key: str, values: Optional[list] = None,
                 description: Optional[str] = None,
                 uncertainties: Optional[list] = None,
                 properties: Optional[list] = None,
                 contents: Optional[list] = None,
                 axis: Optional[str] = None, size: Optional[int] = None,
                 id: Optional[str] = None, ref: Optional[str] = None,
                 encryption: Optional[EncryptionType] = None,
                 format_string: Optional[str] = None):
        super().__init__(key, values, description, uncertainties, properties,
                          contents, axis, size, id, ref, encryption)
        self.format_string = format_string


class _NumericContentList(_ContentListBase):
    """Base for numeric content list types with units/scaleFactor."""
    def __init__(self, key: str, values: Optional[list] = None,
                 description: Optional[str] = None,
                 uncertainties: Optional[list] = None,
                 properties: Optional[list] = None,
                 contents: Optional[list] = None,
                 axis: Optional[str] = None, size: Optional[int] = None,
                 id: Optional[str] = None, ref: Optional[str] = None,
                 encryption: Optional[EncryptionType] = None,
                 format_string: Optional[str] = None,
                 units: Optional[str] = None,
                 scale_factor: Optional[float] = None):
        super().__init__(key, values, description, uncertainties, properties,
                          contents, axis, size, id, ref, encryption)
        self.format_string = format_string
        self.units = units
        self.scale_factor = scale_factor


class ContentDecimalListType(_NumericContentList):
    """Content: list of xs:decimal."""

class ContentDoubleListType(_NumericContentList):
    """Content: list of xs:double."""

class ContentFloatListType(_NumericContentList):
    """Content: list of xs:float."""

class ContentIntListType(_NumericContentList):
    """Content: list of xs:int."""

class ContentLongListType(_NumericContentList):
    """Content: list of xs:long."""

class ContentShortListType(_NumericContentList):
    """Content: list of xs:short."""

class ContentByteListType(_NumericContentList):
    """Content: list of xs:byte."""

class ContentUnsignedIntListType(_NumericContentList):
    """Content: list of xs:unsignedInt."""

class ContentUnsignedLongListType(_NumericContentList):
    """Content: list of xs:unsignedLong."""

class ContentUnsignedShortListType(_NumericContentList):
    """Content: list of xs:unsignedShort."""

class ContentUnsignedByteListType(_NumericContentList):
    """Content: list of xs:unsignedByte."""


class ContentBooleanListType(_ContentListBase):
    """Content: list of xs:boolean."""

class ContentBase64BinaryListType(_ContentListBase):
    """Content: list of xs:base64Binary."""

class ContentHexBinaryListType(_ContentListBase):
    """Content: list of xs:hexBinary."""

class ContentUriListType(_ContentListBase):
    """Content: list of xs:anyURI."""

class ContentUuidListType(_ContentListBase):
    """Content: list of MaiML uuid."""

class ContentLanguageListType(_ContentListBase):
    """Content: list of xs:language."""

class ContentStringEnumType(_ContentListBase):
    """Content: enumeration of xs:string values."""


__all__ = [
    "UncertaintyBaseType", "PropertyBaseType", "ContentBaseType",
    # scalar property
    "StringType", "TokenType", "IdType", "IdRefType", "QualifiedNameType",
    "DateTimeType", "DecimalType", "DoubleType", "FloatType",
    "IntType", "LongType", "ShortType", "ByteType",
    "UnsignedIntType", "UnsignedLongType", "UnsignedShortType", "UnsignedByteType",
    "BooleanType", "Base64BinaryType", "HexBinaryType",
    "UriType", "UuidType", "LanguageType",
    # list property
    "PropertyListType", "StringListType", "IdRefListType", "QualifiedNameListType",
    "DateTimeListType", "DecimalListType", "DoubleListType", "FloatListType",
    "IntListType", "LongListType", "ShortListType", "ByteListType",
    "UnsignedIntListType", "UnsignedLongListType", "UnsignedShortListType", "UnsignedByteListType",
    "BooleanListType", "Base64BinaryListType", "HexBinaryListType",
    "UriListType", "UuidListType", "LanguageListType", "StringEnumType",
    # content list
    "ContentStringListType", "ContentIdRefListType", "ContentQualifiedNameListType",
    "ContentDateTimeListType", "ContentDecimalListType", "ContentDoubleListType",
    "ContentFloatListType", "ContentIntListType", "ContentLongListType",
    "ContentShortListType", "ContentByteListType",
    "ContentUnsignedIntListType", "ContentUnsignedLongListType",
    "ContentUnsignedShortListType", "ContentUnsignedByteListType",
    "ContentBooleanListType", "ContentBase64BinaryListType", "ContentHexBinaryListType",
    "ContentUriListType", "ContentUuidListType", "ContentLanguageListType",
    "ContentStringEnumType",
]
