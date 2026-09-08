"""Tests for _StrictAttributesMixin (maiml_domain.core).

External PyMaiML review finding 10 (2026-09-07): domain classes accepted
any attribute name via plain assignment, so a typo or misplaced field
(e.g. `results.insertions = [...]` where the correct location is
`results.content.insertions`) silently succeeded and was silently ignored
by every consumer that only reads declared fields -- no exception
anywhere pointed at the mistake. These tests exercise the fix
(_StrictAttributesMixin, added to every custom-__init__ base class and
every @dataclass in maiml_domain) end to end.
"""
from __future__ import annotations

import copy
import datetime as dt

import pytest

import maiml_domain as m

UUID = "12345678-1234-3234-8234-123456789012"


def _content(**kwargs):
    kwargs.setdefault("uuid", m.Uuid(UUID))
    return m.GlobalObjectContent(**kwargs)


def _minimal_document():
    vendor = m.VendorType(id="v1", content=_content())
    owner = m.OwnerType(id="o1", content=_content())
    creator = m.CreatorType(
        id="c1",
        vendor_refs=[m.VendorRefType(id="ref1", ref="v1")],
        content=_content(),
    )
    return m.DocumentType(
        id="d1",
        date=dt.datetime.now(dt.timezone.utc),
        creators=[creator], vendors=[vendor], owners=[owner],
        content=_content(),
    )


# ---------------------------------------------------------------------------
# The exact scenario from the review
# ---------------------------------------------------------------------------

def test_misplaced_attribute_on_custom_init_class_is_rejected():
    """The review's own example: `insertions` belongs on
    ResultsType.content, not on ResultsType itself."""
    results = m.ResultsType(id="r1", materials=[], content=_content())
    with pytest.raises(AttributeError, match="insertions"):
        results.insertions = ["oops"]


def test_correct_location_for_the_same_field_still_works():
    results = m.ResultsType(id="r1", materials=[], content=_content())
    results.content.insertions = [
        m.InsertionType(uri="http://example.org/x", hash=m.HashType(value=b"\x00"))
    ]
    assert len(results.content.insertions) == 1


# ---------------------------------------------------------------------------
# Typo'd / unknown attribute names are rejected across every family of
# custom-__init__ base class this package has (HasIdAttributeType,
# RootObjectType, AttributableType, UncertaintyBaseType, and the two
# standalone classes with no shared base at all).
# ---------------------------------------------------------------------------

def test_typo_on_has_id_attribute_type_subclass_is_rejected():
    doc = _minimal_document()
    with pytest.raises(AttributeError, match="dat"):
        doc.dat = dt.datetime.now()


def test_typo_on_uncertainty_base_type_subclass_is_rejected():
    prop = m.StringType(key="ex:k", value="hello")
    with pytest.raises(AttributeError, match="vlaue"):
        prop.vlaue = "typo'd"


def test_typo_on_standalone_extension_type_is_rejected():
    ext = m.ExtensionType(name="concept", prefix="concept",
                           uri="http://www.xes-standard.org/concept.xesext#")
    with pytest.raises(AttributeError, match="nam"):
        ext.nam = "typo'd"


def test_typo_on_root_object_type_subclass_is_rejected():
    doc = _minimal_document()
    # a minimal protocol-only root is enough to exercise RootObjectType
    from maiml_domain import ProtocolFileRootType
    place = m.PlaceType(id="p1")
    trans = m.TransitionType(id="t1")
    arc = m.ArcType(id="a1", source="p1", target="t1")
    pnml = m.PnmlType(id="pn1", places=[place], transitions=[trans], arcs=[arc], content=_content())
    instr = m.InstructionType(id="i1", transition_refs=[m.TransitionRefType(id="ref1", ref="t1")], content=_content())
    program = m.ProgramType(id="prog1", instructions=[instr], content=_content())
    method = m.MethodType(id="m1", pnmls=[pnml], programs=[program], content=_content())
    mt = m.MaterialTemplateType(id="mt1", place_refs=[m.PlaceRefType(id="ref2", ref="p1")], content=_content())
    protocol = m.ProtocolType(id="proto1", methods=[method], material_templates=[mt], content=_content())
    root = ProtocolFileRootType(document=doc, protocol=protocol)
    with pytest.raises(AttributeError, match="documnet"):
        root.documnet = doc


# ---------------------------------------------------------------------------
# @dataclass-based classes get the same guard.
# ---------------------------------------------------------------------------

def test_typo_on_dataclass_based_class_is_rejected():
    goc = _content()
    with pytest.raises(AttributeError, match="insertion"):
        goc.insertion = []  # correct name is 'insertions' (plural)


def test_legitimate_field_on_dataclass_based_class_still_settable():
    goc = _content()
    goc.name = "renamed"
    assert goc.name == "renamed"


# ---------------------------------------------------------------------------
# Regression: a subclass that deliberately narrows its own __init__
# signature (no longer accepting a parameter its parent class does) can
# still set that attribute internally via super().__init__(...). Checking
# only the leaf class's own __init__ signature would wrongly reject this;
# the whitelist must union every __init__ in the MRO. PropertyListType is
# exactly this case: it accepts no 'values' parameter of its own, but
# _PropertyListBase.__init__ (called via super()) still sets self.values.
# ---------------------------------------------------------------------------

def test_attribute_set_by_a_parent_init_under_a_narrowed_subclass_is_allowed():
    plist = m.PropertyListType(key="ex:group", properties=[m.StringType(key="ex:child", value="x")])
    assert plist.values == []  # set internally by _PropertyListBase.__init__


# ---------------------------------------------------------------------------
# The guard must not break copy.deepcopy() -- PyMaiML's
# dumps(drop_stale_signature=...) depends on deepcopy()'ing a loaded
# object tree, and Python's default deepcopy reconstructs instances by
# writing __dict__ directly rather than through setattr(), so this should
# already work, but it is exactly the kind of interaction a hand-written
# __setattr__ guard can silently break -- worth asserting explicitly.
# ---------------------------------------------------------------------------

def test_deepcopy_still_works_on_a_guarded_object():
    doc = _minimal_document()
    doc_copy = copy.deepcopy(doc)
    assert doc_copy is not doc
    assert doc_copy.date == doc.date
    # the copy is independently mutable afterwards, through the normal,
    # legitimate attribute-assignment path
    doc_copy.date = doc.date.replace(year=doc.date.year + 1)
    assert doc_copy.date != doc.date


# ---------------------------------------------------------------------------
# Internal, leading-underscore attributes (e.g. HasIdAttributeType's
# private _id, backing the read-only `id` property) are unaffected --
# both by remaining settable internally, and by the property itself still
# rejecting external reassignment exactly as before this change.
# ---------------------------------------------------------------------------

def test_id_property_still_has_no_public_setter():
    doc = _minimal_document()
    with pytest.raises(AttributeError):
        doc.id = "new-id"
