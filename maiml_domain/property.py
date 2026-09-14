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

from .core import EncryptionType, _StrictAttributesMixin
from .simple_types import UUID_PATTERN


# ---------------------------------------------------------------------------
# Lexical (XSD simpleType) validation helpers
# ---------------------------------------------------------------------------
#
# External review finding: scalar `value`/`values` previously accepted any
# Python object (e.g. IntType(value="not-an-int") constructed without
# error), and `properties`/`contents`/`uncertainties` accepted any object as
# a list element (e.g. properties=[object()] constructed without error).
# Both are lexical/structural constraints a single complexType definition
# determines by itself -- squarely inside this repository's validation scope
# (see README.md's "バリデーションの範囲") -- so they belong here, not left for
# downstream SDKs to discover as an opaque XSD validation failure.

# xs:byte / xs:short / xs:int / xs:long and their unsigned counterparts:
# inclusive [min, max] lexical ranges.
_XS_BYTE_RANGE = (-128, 127)
_XS_SHORT_RANGE = (-32768, 32767)
_XS_INT_RANGE = (-2147483648, 2147483647)
_XS_LONG_RANGE = (-9223372036854775808, 9223372036854775807)
_XS_UNSIGNED_BYTE_RANGE = (0, 255)
_XS_UNSIGNED_SHORT_RANGE = (0, 65535)
_XS_UNSIGNED_INT_RANGE = (0, 4294967295)
_XS_UNSIGNED_LONG_RANGE = (0, 18446744073709551615)


def _check_int_range(cls_name: str, value: int, range_: tuple, *, label: str = "value") -> None:
    lo, hi = range_
    if not (lo <= value <= hi):
        raise ValueError(
            f"{cls_name}.{label} is out of range: {value!r} (must satisfy "
            f"{lo} <= {label} <= {hi}, per this type's XSD lexical space)"
        )


def _check_uuid_lexical(cls_name: str, value: str, *, label: str = "value") -> None:
    if not UUID_PATTERN.match(value):
        raise ValueError(f"{cls_name}.{label} is not a valid MaiML UUID: {value!r}")


def _check_decimal_finite(cls_name: str, value: Any, *, label: str = "value") -> None:
    """xs:decimal's value space (unlike xs:float/xs:double) does not include
    NaN, INF or -INF -- only Decimal instances are checked here since a plain
    int (also accepted by DecimalType/-ListType) is always finite."""
    if isinstance(value, Decimal) and not value.is_finite():
        raise ValueError(
            f"{cls_name}.{label} must be finite for xs:decimal (NaN/Infinity/"
            f"-Infinity are not part of xs:decimal's value space): {value!r}"
        )


def _check_list_element_types(cls_name: str, items: list, expected_type: type, label: str) -> None:
    """properties/contents/uncertainties: each element must be an instance
    of expected_type (PropertyBaseType/ContentBaseType/UncertaintyBaseType
    respectively, per maiml-property.xsd's property/content/uncertainty
    element declarations) -- not merely "something in a list"."""
    for item in items:
        if not isinstance(item, expected_type):
            raise TypeError(
                f"{cls_name}.{label} elements must be {expected_type.__name__} "
                f"instances, got {type(item).__name__}: {item!r}"
            )


def _check_encryption_exclusive(instance, encryption, has_plain_content, plain_content_label: str) -> None:
    """Every concrete property*/content* type's XSD definition offers an
    xs:choice between plain content and encryptionGroup (see this module's
    docstring) -- 'encryption' must never be combined with any plain-
    content field. Extracted once here because _ScalarPropertyBase,
    _PropertyListBase and _ContentListBase each independently repeated the
    identical check (external review finding: 3 duplicate copies)."""
    if encryption is not None and has_plain_content:
        raise ValueError(
            f"{type(instance).__name__}: 'encryption' cannot be combined "
            f"with {plain_content_label} -- this type's XSD definition "
            "models the two as an xs:choice."
        )


# ---------------------------------------------------------------------------
# Abstract bases
# ---------------------------------------------------------------------------

class UncertaintyBaseType(_StrictAttributesMixin, ABC):
    """
    Root abstract type for both property and content.
    Carries a required 'key' attribute (xs:QName stored as str) and the
    optional EncryptionType payload shared by every property*/content* type.
    """

    # Concrete scalar/list leaf classes declare the Python type(s) their
    # `value`/`values` element must be an instance of (empty tuple = no
    # check -- left as-is for abstract/container-only classes such as
    # PropertyListType, which never carries a real value).
    _value_types: tuple = ()
    # bool is a subclass of int in Python; numeric leaf classes that must
    # NOT accept a bool where an int/float is expected set this True (see
    # pymaiml.builders._SCALAR_CLASS_BY_TYPE's own comment for the same
    # concern on the SDK side).
    _reject_bool: bool = False

    def __init__(self, key: str, encryption: Optional[EncryptionType] = None):
        if not key:
            raise ValueError("key must not be empty")
        self.key: str = key
        self.encryption: Optional[EncryptionType] = encryption

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(key={self.key!r})"

    def _check_value(self, value: Any, *, label: str = "value") -> None:
        """Validate one scalar value (or one element of a `values` list)
        against this class's declared lexical constraints. Called for each
        non-None scalar `value` and for each element of a list `values`."""
        cls_name = type(self).__name__
        if self._reject_bool and isinstance(value, bool):
            raise TypeError(
                f"{cls_name}.{label} must not be bool -- xs:boolean and "
                "this type's own XSD primitive type are lexically distinct "
                "(Python bool is a subclass of int, which would otherwise "
                "let a boolean silently pass as an integer)."
            )
        if self._value_types and not isinstance(value, self._value_types):
            type_names = "/".join(t.__name__ for t in self._value_types)
            raise TypeError(
                f"{cls_name}.{label} must be {type_names}, got "
                f"{type(value).__name__}: {value!r}"
            )
        self._check_value_extra(value, label=label)

    def _check_value_extra(self, value: Any, *, label: str = "value") -> None:
        """Hook for constraints beyond a plain Python isinstance() check
        (numeric range, UUID pattern, ...). No-op unless overridden."""
        pass


class PropertyBaseType(UncertaintyBaseType, ABC):
    """Abstract base for all property types."""
    pass


class ContentBaseType(UncertaintyBaseType, ABC):
    """
    Abstract base for all content types.
    Adds axis, size, id, ref attributes (all optional).

    id/ref are xs:ID/xs:IDREF (maiml-property.xsd's contentBaseType), the
    same lexical types as HasIdAttributeType.id (maiml-helper.xsd) --
    xs:ID/xs:IDREF derive from xs:NCName, whose lexical space excludes the
    empty string. Previously only HasIdAttributeType enforced this, so
    ContentBaseType.id/ref silently accepted "" where HasIdAttributeType.id
    would reject it -- the same XSD-level constraint enforced
    inconsistently depending on which class happened to carry it.
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
        if id is not None and id == "":
            raise ValueError(f"{type(self).__name__}.id must not be empty (xs:ID)")
        if ref is not None and ref == "":
            raise ValueError(f"{type(self).__name__}.ref must not be empty (xs:IDREF)")
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
        if value is not None:
            self._check_value(value)
        self.value = value
        self.description = description
        self.uncertainties: list = uncertainties or []
        self.properties: list = properties or []
        self.contents: list = contents or []
        _check_list_element_types(type(self).__name__, self.uncertainties, UncertaintyBaseType, "uncertainties")
        _check_list_element_types(type(self).__name__, self.properties, PropertyBaseType, "properties")
        _check_list_element_types(type(self).__name__, self.contents, ContentBaseType, "contents")
        _check_encryption_exclusive(
            self, encryption,
            value is not None or description is not None
            or self.uncertainties or self.properties or self.contents,
            "value/description/uncertainty/property/content",
        )

    def __repr__(self):
        return f"{self.__class__.__name__}(key={self.key!r}, value={self.value!r})"


class StringType(_ScalarPropertyBase):
    """Property: xs:string scalar."""
    _value_types = (str,)

class TokenType(_ScalarPropertyBase):
    """Property: xs:token scalar."""
    _value_types = (str,)

class IdType(_ScalarPropertyBase):
    """Property: xs:ID scalar (nillable)."""
    _value_types = (str,)

class IdRefType(_ScalarPropertyBase):
    """Property: xs:IDREF scalar (nillable)."""
    _value_types = (str,)

class QualifiedNameType(_ScalarPropertyBase):
    """Property: xs:QName scalar (nillable)."""
    _value_types = (str,)


class DateTimeType(_ScalarPropertyBase):
    """Property: xs:dateTime scalar (nillable). Optional formatString attribute."""
    _value_types = (datetime,)

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
    _value_types = (Decimal, int)
    _reject_bool = True

    def _check_value_extra(self, value, *, label="value"):
        _check_decimal_finite(type(self).__name__, value, label=label)

class DoubleType(_NumericScalarPropertyBase):
    """Property: xs:double scalar. Optional formatString, units, scaleFactor."""
    _value_types = (float, int)
    _reject_bool = True

class FloatType(_NumericScalarPropertyBase):
    """Property: xs:float scalar. Optional formatString, units, scaleFactor."""
    _value_types = (float, int)
    _reject_bool = True

class IntType(_NumericScalarPropertyBase):
    """Property: xs:int scalar. Optional formatString, units, scaleFactor."""
    _value_types = (int,)
    _reject_bool = True

    def _check_value_extra(self, value, *, label="value"):
        _check_int_range(type(self).__name__, value, _XS_INT_RANGE, label=label)

class LongType(_NumericScalarPropertyBase):
    """Property: xs:long scalar."""
    _value_types = (int,)
    _reject_bool = True

    def _check_value_extra(self, value, *, label="value"):
        _check_int_range(type(self).__name__, value, _XS_LONG_RANGE, label=label)

class ShortType(_NumericScalarPropertyBase):
    """Property: xs:short scalar."""
    _value_types = (int,)
    _reject_bool = True

    def _check_value_extra(self, value, *, label="value"):
        _check_int_range(type(self).__name__, value, _XS_SHORT_RANGE, label=label)

class ByteType(_NumericScalarPropertyBase):
    """Property: xs:byte scalar."""
    _value_types = (int,)
    _reject_bool = True

    def _check_value_extra(self, value, *, label="value"):
        _check_int_range(type(self).__name__, value, _XS_BYTE_RANGE, label=label)

class UnsignedIntType(_NumericScalarPropertyBase):
    """Property: xs:unsignedInt scalar."""
    _value_types = (int,)
    _reject_bool = True

    def _check_value_extra(self, value, *, label="value"):
        _check_int_range(type(self).__name__, value, _XS_UNSIGNED_INT_RANGE, label=label)

class UnsignedLongType(_NumericScalarPropertyBase):
    """Property: xs:unsignedLong scalar."""
    _value_types = (int,)
    _reject_bool = True

    def _check_value_extra(self, value, *, label="value"):
        _check_int_range(type(self).__name__, value, _XS_UNSIGNED_LONG_RANGE, label=label)

class UnsignedShortType(_NumericScalarPropertyBase):
    """Property: xs:unsignedShort scalar."""
    _value_types = (int,)
    _reject_bool = True

    def _check_value_extra(self, value, *, label="value"):
        _check_int_range(type(self).__name__, value, _XS_UNSIGNED_SHORT_RANGE, label=label)

class UnsignedByteType(_NumericScalarPropertyBase):
    """Property: xs:unsignedByte scalar."""
    _value_types = (int,)
    _reject_bool = True

    def _check_value_extra(self, value, *, label="value"):
        _check_int_range(type(self).__name__, value, _XS_UNSIGNED_BYTE_RANGE, label=label)


class BooleanType(_ScalarPropertyBase):
    """Property: xs:boolean scalar."""
    _value_types = (bool,)

class Base64BinaryType(_ScalarPropertyBase):
    """Property: xs:base64Binary scalar."""
    _value_types = (bytes, bytearray)

class HexBinaryType(_ScalarPropertyBase):
    """Property: xs:hexBinary scalar."""
    _value_types = (bytes, bytearray)

class UriType(_ScalarPropertyBase):
    """Property: xs:anyURI scalar."""
    _value_types = (str,)

class UuidType(_ScalarPropertyBase):
    """Property: MaiML uuid scalar (nillable)."""
    _value_types = (str,)

    def _check_value_extra(self, value, *, label="value"):
        _check_uuid_lexical(type(self).__name__, value, label=label)

class LanguageType(_ScalarPropertyBase):
    """Property: xs:language scalar (nillable)."""
    _value_types = (str,)


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
        self.values: List[Any] = list(values) if values else []
        for _v in self.values:
            self._check_value(_v, label="values element")
        self.description = description
        self.uncertainties: list = uncertainties or []
        self.properties: list = properties or []
        self.contents: list = contents or []
        _check_list_element_types(type(self).__name__, self.uncertainties, UncertaintyBaseType, "uncertainties")
        _check_list_element_types(type(self).__name__, self.properties, PropertyBaseType, "properties")
        _check_list_element_types(type(self).__name__, self.contents, ContentBaseType, "contents")
        _check_encryption_exclusive(
            self, encryption,
            self.values or description is not None
            or self.uncertainties or self.properties or self.contents,
            "values/description/uncertainty/property/content",
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
    _value_types = (str,)

class IdRefListType(_PropertyListBase):
    """Property: list of xs:IDREF."""
    _value_types = (str,)

class QualifiedNameListType(_PropertyListBase):
    """Property: list of xs:QName."""
    _value_types = (str,)


class DateTimeListType(_PropertyListBase):
    """Property: list of xs:dateTime. Optional formatString."""
    _value_types = (datetime,)

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
    _value_types = (Decimal, int)
    _reject_bool = True

    def _check_value_extra(self, value, *, label="value"):
        _check_decimal_finite(type(self).__name__, value, label=label)

class DoubleListType(_NumericListProperty):
    """Property: list of xs:double."""
    _value_types = (float, int)
    _reject_bool = True

class FloatListType(_NumericListProperty):
    """Property: list of xs:float."""
    _value_types = (float, int)
    _reject_bool = True

class IntListType(_NumericListProperty):
    """Property: list of xs:int."""
    _value_types = (int,)
    _reject_bool = True

    def _check_value_extra(self, value, *, label="value"):
        _check_int_range(type(self).__name__, value, _XS_INT_RANGE, label=label)

class LongListType(_NumericListProperty):
    """Property: list of xs:long."""
    _value_types = (int,)
    _reject_bool = True

    def _check_value_extra(self, value, *, label="value"):
        _check_int_range(type(self).__name__, value, _XS_LONG_RANGE, label=label)

class ShortListType(_NumericListProperty):
    """Property: list of xs:short."""
    _value_types = (int,)
    _reject_bool = True

    def _check_value_extra(self, value, *, label="value"):
        _check_int_range(type(self).__name__, value, _XS_SHORT_RANGE, label=label)

class ByteListType(_NumericListProperty):
    """Property: list of xs:byte."""
    _value_types = (int,)
    _reject_bool = True

    def _check_value_extra(self, value, *, label="value"):
        _check_int_range(type(self).__name__, value, _XS_BYTE_RANGE, label=label)

class UnsignedIntListType(_NumericListProperty):
    """Property: list of xs:unsignedInt."""
    _value_types = (int,)
    _reject_bool = True

    def _check_value_extra(self, value, *, label="value"):
        _check_int_range(type(self).__name__, value, _XS_UNSIGNED_INT_RANGE, label=label)

class UnsignedLongListType(_NumericListProperty):
    """Property: list of xs:unsignedLong."""
    _value_types = (int,)
    _reject_bool = True

    def _check_value_extra(self, value, *, label="value"):
        _check_int_range(type(self).__name__, value, _XS_UNSIGNED_LONG_RANGE, label=label)

class UnsignedShortListType(_NumericListProperty):
    """Property: list of xs:unsignedShort."""
    _value_types = (int,)
    _reject_bool = True

    def _check_value_extra(self, value, *, label="value"):
        _check_int_range(type(self).__name__, value, _XS_UNSIGNED_SHORT_RANGE, label=label)

class UnsignedByteListType(_NumericListProperty):
    """Property: list of xs:unsignedByte."""
    _value_types = (int,)
    _reject_bool = True

    def _check_value_extra(self, value, *, label="value"):
        _check_int_range(type(self).__name__, value, _XS_UNSIGNED_BYTE_RANGE, label=label)


class BooleanListType(_PropertyListBase):
    """Property: list of xs:boolean."""
    _value_types = (bool,)

class Base64BinaryListType(_PropertyListBase):
    """Property: list of xs:base64Binary."""
    _value_types = (bytes, bytearray)

class HexBinaryListType(_PropertyListBase):
    """Property: list of xs:hexBinary."""
    _value_types = (bytes, bytearray)

class UriListType(_PropertyListBase):
    """Property: list of xs:anyURI."""
    _value_types = (str,)

class UuidListType(_PropertyListBase):
    """Property: list of MaiML uuid."""
    _value_types = (str,)

    def _check_value_extra(self, value, *, label="value"):
        _check_uuid_lexical(type(self).__name__, value, label=label)

class LanguageListType(_PropertyListBase):
    """Property: list of xs:language."""
    _value_types = (str,)

class StringEnumType(_PropertyListBase):
    """Property: enumeration of xs:string values."""
    _value_types = (str,)


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
        self.values: List[Any] = list(values) if values else []
        for _v in self.values:
            self._check_value(_v, label="values element")
        self.description = description
        self.uncertainties: list = uncertainties or []
        self.properties: list = properties or []
        self.contents: list = contents or []
        _check_list_element_types(type(self).__name__, self.uncertainties, UncertaintyBaseType, "uncertainties")
        _check_list_element_types(type(self).__name__, self.properties, PropertyBaseType, "properties")
        _check_list_element_types(type(self).__name__, self.contents, ContentBaseType, "contents")
        _check_encryption_exclusive(
            self, encryption,
            self.values or description is not None
            or self.uncertainties or self.properties or self.contents,
            "values/description/uncertainty/property/content",
        )

    def __repr__(self):
        return f"{self.__class__.__name__}(key={self.key!r}, values={self.values!r})"


class ContentStringListType(_ContentListBase):
    """Content: list of xs:string."""
    _value_types = (str,)

class ContentIdRefListType(_ContentListBase):
    """Content: list of xs:IDREF."""
    _value_types = (str,)

class ContentQualifiedNameListType(_ContentListBase):
    """Content: list of xs:QName."""
    _value_types = (str,)


class ContentDateTimeListType(_ContentListBase):
    """Content: list of xs:dateTime. Optional formatString."""
    _value_types = (datetime,)

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
    _value_types = (Decimal, int)
    _reject_bool = True

    def _check_value_extra(self, value, *, label="value"):
        _check_decimal_finite(type(self).__name__, value, label=label)

class ContentDoubleListType(_NumericContentList):
    """Content: list of xs:double."""
    _value_types = (float, int)
    _reject_bool = True

class ContentFloatListType(_NumericContentList):
    """Content: list of xs:float."""
    _value_types = (float, int)
    _reject_bool = True

class ContentIntListType(_NumericContentList):
    """Content: list of xs:int."""
    _value_types = (int,)
    _reject_bool = True

    def _check_value_extra(self, value, *, label="value"):
        _check_int_range(type(self).__name__, value, _XS_INT_RANGE, label=label)

class ContentLongListType(_NumericContentList):
    """Content: list of xs:long."""
    _value_types = (int,)
    _reject_bool = True

    def _check_value_extra(self, value, *, label="value"):
        _check_int_range(type(self).__name__, value, _XS_LONG_RANGE, label=label)

class ContentShortListType(_NumericContentList):
    """Content: list of xs:short."""
    _value_types = (int,)
    _reject_bool = True

    def _check_value_extra(self, value, *, label="value"):
        _check_int_range(type(self).__name__, value, _XS_SHORT_RANGE, label=label)

class ContentByteListType(_NumericContentList):
    """Content: list of xs:byte."""
    _value_types = (int,)
    _reject_bool = True

    def _check_value_extra(self, value, *, label="value"):
        _check_int_range(type(self).__name__, value, _XS_BYTE_RANGE, label=label)

class ContentUnsignedIntListType(_NumericContentList):
    """Content: list of xs:unsignedInt."""
    _value_types = (int,)
    _reject_bool = True

    def _check_value_extra(self, value, *, label="value"):
        _check_int_range(type(self).__name__, value, _XS_UNSIGNED_INT_RANGE, label=label)

class ContentUnsignedLongListType(_NumericContentList):
    """Content: list of xs:unsignedLong."""
    _value_types = (int,)
    _reject_bool = True

    def _check_value_extra(self, value, *, label="value"):
        _check_int_range(type(self).__name__, value, _XS_UNSIGNED_LONG_RANGE, label=label)

class ContentUnsignedShortListType(_NumericContentList):
    """Content: list of xs:unsignedShort."""
    _value_types = (int,)
    _reject_bool = True

    def _check_value_extra(self, value, *, label="value"):
        _check_int_range(type(self).__name__, value, _XS_UNSIGNED_SHORT_RANGE, label=label)

class ContentUnsignedByteListType(_NumericContentList):
    """Content: list of xs:unsignedByte."""
    _value_types = (int,)
    _reject_bool = True

    def _check_value_extra(self, value, *, label="value"):
        _check_int_range(type(self).__name__, value, _XS_UNSIGNED_BYTE_RANGE, label=label)


class ContentBooleanListType(_ContentListBase):
    """Content: list of xs:boolean."""
    _value_types = (bool,)

class ContentBase64BinaryListType(_ContentListBase):
    """Content: list of xs:base64Binary."""
    _value_types = (bytes, bytearray)

class ContentHexBinaryListType(_ContentListBase):
    """Content: list of xs:hexBinary."""
    _value_types = (bytes, bytearray)

class ContentUriListType(_ContentListBase):
    """Content: list of xs:anyURI."""
    _value_types = (str,)

class ContentUuidListType(_ContentListBase):
    """Content: list of MaiML uuid."""
    _value_types = (str,)

    def _check_value_extra(self, value, *, label="value"):
        _check_uuid_lexical(type(self).__name__, value, label=label)

class ContentLanguageListType(_ContentListBase):
    """Content: list of xs:language."""
    _value_types = (str,)

class ContentStringEnumType(_ContentListBase):
    """Content: enumeration of xs:string values."""
    _value_types = (str,)


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
