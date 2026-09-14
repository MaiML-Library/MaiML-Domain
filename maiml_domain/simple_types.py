"""
MaiML Simple Types
Corresponds to: maiml-simpleTypes.xsd
"""

import re

# --- UUID (RFC pattern: v3/v4/v5 only) ---
UUID_PATTERN = re.compile(
    r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[3-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$'
)


# --- NCName (XML 1.0 sec. 2.3 / Namespaces in XML sec. 3) ---
# xs:ID / xs:IDREF derive from xs:NCName. This pattern covers the Basic
# Multilingual Plane NameStartChar/NameChar ranges from the XML Name
# production; it does not special-case the astral-plane range
# #x10000-#xEFFFF (irrelevant for MaiML's ASCII-oriented id/ref values in
# practice, and awkward to express as a plain `re` character class).
_NC_NAME_START_CHARS = (
    r"A-Za-z_"
    r"\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF"
    r"\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD"
)
_NC_NAME_CHAR_EXTRA = r"0-9\u00B7\u0300-\u036F\u203F-\u2040.\-"
NCNAME_PATTERN = re.compile(
    "^[" + _NC_NAME_START_CHARS + "][" + _NC_NAME_START_CHARS + _NC_NAME_CHAR_EXTRA + "]*$"
)

# --- xs:language (W3C XML Schema builtin type's own pattern facet) ---
# This is the literal facet the XSD spec itself uses to constrain
# xs:language -- syntactic (RFC 3066-shaped tag), not a check against an
# actual language-subtag registry (deliberately out of Domain's scope, see
# README.md's "バリデーションの範囲").
LANGUAGE_TAG_PATTERN = re.compile(r'^[a-zA-Z]{1,8}(-[a-zA-Z0-9]{1,8})*$')

class Uuid(str):
    """UUID string restricted to versions 3, 4, 5 (RFC 4122)."""

    def __new__(cls, value: str) -> "Uuid":
        if not UUID_PATTERN.match(value):
            raise ValueError(
                f"Invalid MaiML UUID: '{value}'. "
                "Must match pattern [0-9a-fA-F]{8}-...-[3-5]xxx-[89abAB]xxx-..."
            )
        return super().__new__(cls, value)

    def __repr__(self) -> str:
        return f"Uuid('{self}')"


class IsoLanguageName(str):
    """ISO language code: 2 or 3 lowercase/uppercase ASCII letters."""

    _PATTERN = re.compile(r'^[a-zA-Z]{2,3}$')

    def __new__(cls, value: str) -> "IsoLanguageName":
        if not cls._PATTERN.match(value):
            raise ValueError(f"Invalid IsoLanguageName: '{value}'")
        return super().__new__(cls, value)


class DecimalFormatString(str):
    """Format string for decimal: '0' or '0.0', '0.00', etc."""

    _PATTERN = re.compile(r'^0(\.0+)?$')

    def __new__(cls, value: str) -> "DecimalFormatString":
        if not cls._PATTERN.match(value):
            raise ValueError(f"Invalid DecimalFormatString: '{value}'")
        return super().__new__(cls, value)


class FloatFormatString(str):
    """Format string for float/double: '0', '0.0', '0.0E0', etc."""

    def __new__(cls, value: str) -> "FloatFormatString":
        if not re.match(r'^0(\.0+)?((E|e)0+)?$', value):
            raise ValueError(f"Invalid FloatFormatString: '{value}'")
        return super().__new__(cls, value)


class IntegerFormatString(str):
    """Format string for integer: must be exactly '0'."""

    def __new__(cls, value: str) -> "IntegerFormatString":
        if value != "0":
            raise ValueError(f"Invalid IntegerFormatString: '{value}' (must be '0')")
        return super().__new__(cls, value)


class DateTimeFormatString(str):
    """
    Format string for dateTime.

    maiml-simpleTypes.xsd's dateTimeFormatStringType pattern is written using
    the literal placeholder notation from the W3C NOTE on date/time formats
    (https://www.w3.org/TR/NOTE-datetime) rather than a real regular
    expression for an actual timestamp: the only valid values are the
    literal string 'YYYY-MM-DDThh:mm:ss', optionally followed by a literal
    '.' plus one or more literal 's' characters (a fractional-second
    placeholder) and/or the literal string 'TZD' (a timezone-designator
    placeholder). Any other value is rejected.
    """

    _PATTERN = re.compile(r'^YYYY-MM-DDThh:mm:ss(\.s+)?(TZD)?$')

    def __new__(cls, value: str) -> "DateTimeFormatString":
        if not cls._PATTERN.match(value):
            raise ValueError(
                f"Invalid DateTimeFormatString: '{value}'. Must be the "
                "literal placeholder pattern 'YYYY-MM-DDThh:mm:ss[.s+][TZD]' "
                "defined by maiml-simpleTypes.xsd "
                "(see https://www.w3.org/TR/NOTE-datetime)."
            )
        return super().__new__(cls, value)


__all__ = [
    "Uuid", "IsoLanguageName", "DecimalFormatString",
    "FloatFormatString", "IntegerFormatString", "DateTimeFormatString",
    "NCNAME_PATTERN", "LANGUAGE_TAG_PATTERN",
]
