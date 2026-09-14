"""Regression tests for maiml_domain/property.py's lexical & structural
validation (scalar `value` type/range/UUID checks, `properties`/`contents`/
`uncertainties` element-type checks, `ContentBaseType.id`/`ref` empty-string
rejection, encryption/plain-content exclusivity, and xs:decimal finiteness).

Added per MaiML_Domain_new_required_fixes.md (2 - "今回追加したDomain検証の
専用回帰テストを追加する") and item 1 of the same document (DecimalType /
DecimalListType finite-value rejection). Prior to this file, these checks
were only exercised indirectly via tests/build_sample_maiml.py's happy-path
construction -- a passing smoke test does not pin "invalid values are
rejected", so a future refactor of property.py could silently drop one of
these checks without any test failing. Each test below targets exactly one
constraint so a regression points straight at its cause.

test_strict_attributes.py covers a different concern (_StrictAttributesMixin
rejecting undeclared attribute names) and is not duplicated here.
"""
from __future__ import annotations

from decimal import Decimal

import pytest

import maiml_domain as m


def _encryption():
    return m.EncryptionType(encrypted_data="<xenc:EncryptedData>...</xenc:EncryptedData>")


# ---------------------------------------------------------------------------
# Scalar `value`: Python-type checks (TypeError)
# ---------------------------------------------------------------------------

def test_int_type_rejects_string():
    with pytest.raises(TypeError):
        m.IntType(key="x", value="not-an-int")


def test_int_type_rejects_bool():
    with pytest.raises(TypeError):
        m.IntType(key="x", value=True)


def test_boolean_type_rejects_string():
    with pytest.raises(TypeError):
        m.BooleanType(key="x", value="yes")


def test_boolean_type_accepts_bool():
    assert m.BooleanType(key="x", value=True).value is True
    assert m.BooleanType(key="x", value=False).value is False


def test_decimal_type_accepts_int_but_rejects_bool():
    assert m.DecimalType(key="x", value=5).value == 5
    with pytest.raises(TypeError):
        m.DecimalType(key="x", value=True)


def test_double_type_rejects_int_as_string_but_not_int_itself():
    # DoubleType/-List accept float or int (xs:double's lexical space
    # includes integral literals); a bool must still be rejected.
    assert m.DoubleType(key="x", value=5).value == 5
    with pytest.raises(TypeError):
        m.DoubleType(key="x", value=True)


# ---------------------------------------------------------------------------
# Scalar `value`: XSD lexical range checks (ValueError)
# ---------------------------------------------------------------------------

def test_int_type_rejects_out_of_range():
    with pytest.raises(ValueError):
        m.IntType(key="x", value=2**31)


def test_int_type_accepts_boundary_values():
    assert m.IntType(key="x", value=2**31 - 1).value == 2**31 - 1
    assert m.IntType(key="x", value=-(2**31)).value == -(2**31)


def test_byte_type_rejects_out_of_range():
    with pytest.raises(ValueError):
        m.ByteType(key="x", value=128)
    with pytest.raises(ValueError):
        m.ByteType(key="x", value=-129)


def test_unsigned_int_type_rejects_negative():
    with pytest.raises(ValueError):
        m.UnsignedIntType(key="x", value=-1)


# ---------------------------------------------------------------------------
# Scalar `value`: xs:decimal must be finite (NaN/Infinity/-Infinity rejected)
# ---------------------------------------------------------------------------

def test_decimal_type_rejects_nan():
    with pytest.raises(ValueError):
        m.DecimalType(key="x", value=Decimal("NaN"))


def test_decimal_type_rejects_positive_infinity():
    with pytest.raises(ValueError):
        m.DecimalType(key="x", value=Decimal("Infinity"))


def test_decimal_type_rejects_negative_infinity():
    with pytest.raises(ValueError):
        m.DecimalType(key="x", value=Decimal("-Infinity"))


def test_decimal_type_accepts_finite_decimal():
    assert m.DecimalType(key="x", value=Decimal("1.50")).value == Decimal("1.50")


def test_decimal_list_type_rejects_non_finite_value():
    with pytest.raises(ValueError):
        m.DecimalListType(key="x", values=[Decimal("1.0"), Decimal("NaN")])


def test_content_decimal_list_type_rejects_non_finite_value():
    with pytest.raises(ValueError):
        m.ContentDecimalListType(key="x", values=[Decimal("Infinity")])


def test_float_type_allows_non_finite_by_design():
    # Contrast case: unlike xs:decimal, xs:float/xs:double's value space
    # DOES include NaN/INF/-INF, so FloatType/DoubleType must NOT reject
    # them (only DecimalType/-List/-ContentList do, per item 1 of
    # MaiML_Domain_new_required_fixes.md).
    assert m.FloatType(key="x", value=float("nan")).value != m.FloatType(key="x", value=float("nan")).value
    assert m.FloatType(key="x", value=float("inf")).value == float("inf")


# ---------------------------------------------------------------------------
# Scalar `value`: UUID lexical check
# ---------------------------------------------------------------------------

def test_uuid_type_rejects_invalid_uuid():
    with pytest.raises(ValueError):
        m.UuidType(key="x", value="not-a-uuid")


def test_uuid_type_accepts_valid_uuid():
    valid = "12345678-1234-4234-8234-123456789012"
    assert m.UuidType(key="x", value=valid).value == valid


# ---------------------------------------------------------------------------
# properties / contents / uncertainties: list-element type checks
# ---------------------------------------------------------------------------

def test_properties_reject_wrong_element_type():
    with pytest.raises(TypeError):
        m.StringType(key="x", properties=[object()])


def test_contents_reject_wrong_element_type():
    with pytest.raises(TypeError):
        m.StringType(key="x", contents=[object()])


def test_uncertainties_reject_wrong_element_type():
    with pytest.raises(TypeError):
        m.StringType(key="x", uncertainties=[object()])


def test_properties_accept_correct_element_type():
    inner = m.StringType(key="inner", value="v")
    outer = m.StringType(key="x", properties=[inner])
    assert outer.properties == [inner]


def test_contents_accept_correct_element_type():
    inner = m.ContentStringListType(key="inner", values=["v"])
    outer = m.StringType(key="x", contents=[inner])
    assert outer.contents == [inner]


def test_list_type_values_element_type_is_checked_too():
    # _PropertyListBase/_ContentListBase check each element of `values`
    # itself (not just properties/contents/uncertainties).
    with pytest.raises(TypeError):
        m.StringListType(key="x", values=[123])


# ---------------------------------------------------------------------------
# ContentBaseType.id / ref: empty string rejected (xs:ID / xs:IDREF)
# ---------------------------------------------------------------------------

def test_content_id_rejects_empty_string():
    with pytest.raises(ValueError):
        m.ContentStringListType(key="x", id="")


def test_content_ref_rejects_empty_string():
    with pytest.raises(ValueError):
        m.ContentStringListType(key="x", ref="")


def test_content_id_accepts_non_empty_string():
    assert m.ContentStringListType(key="x", id="c1").id == "c1"


# ---------------------------------------------------------------------------
# encryption / plain-content exclusivity (xs:choice)
# ---------------------------------------------------------------------------

def test_encryption_cannot_be_combined_with_plain_value():
    with pytest.raises(ValueError):
        m.StringType(key="x", value="plain", encryption=_encryption())


def test_encryption_alone_is_allowed_on_scalar():
    obj = m.StringType(key="x", encryption=_encryption())
    assert obj.encryption is not None
    assert obj.value is None


def test_encryption_cannot_be_combined_with_plain_values_on_list_type():
    with pytest.raises(ValueError):
        m.StringListType(key="x", values=["a"], encryption=_encryption())


def test_encryption_cannot_be_combined_with_plain_values_on_content_list_type():
    with pytest.raises(ValueError):
        m.ContentStringListType(key="x", values=["a"], encryption=_encryption())


def test_encryption_alone_is_allowed_on_content_list_type():
    obj = m.ContentStringListType(key="x", encryption=_encryption())
    assert obj.encryption is not None
    assert obj.values == []
