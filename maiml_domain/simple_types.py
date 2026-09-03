"""
MaiML Simple Types
Corresponds to: maiml-simpleTypes.xsd
"""

import re

# --- UUID (RFC pattern: v3/v4/v5 only) ---
UUID_PATTERN = re.compile(
    r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[3-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$'
)

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
]
