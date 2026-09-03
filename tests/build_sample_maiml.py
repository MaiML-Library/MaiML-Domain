"""
maiml_domain のオブジェクトを実際に組み立てて、MaiML-Schema-1_0 に準拠する
.maiml ファイルを1つ生成する検証用スクリプト。

maiml_domain にはまだ to_xml() のようなシリアライズ機能が無いため、ここでは
「オブジェクトを正しく構築できるか」を maiml_domain 経由で確認したうえで、
その構造をそのまま素直にXMLへ書き出す薄いコンバータをこのファイル限定で
実装している(ライブラリ本体を汚さない、検証専用のテストコード)。

使い方:
    pip install -e .          # リポジトリ直下で(未実施なら)
    python3 tests/build_sample_maiml.py

生成された tests/output/sample.maiml を、MaiML-Schema-1_0 の XSD
(および可能であれば JIS K 0200 の業務ルール検証スクリプト)にかけて
妥当性を確認すること。
"""
from __future__ import annotations

import sys
import uuid as uuidlib
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from xml.dom import minidom
from xml.etree import ElementTree as ET

# リポジトリ直下を sys.path に追加しておく(editable install していなくても動くように)
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import maiml_domain as m  # noqa: E402  (sys.path調整の後に import する)

MAIML_NS = "http://www.maiml.org/schemas"
XSI_NS = "http://www.w3.org/2001/XMLSchema-instance"
EX_NS = "http://example.org/maiml-domain-test"
KYL_NS = "http://example.org/kyl-instrument-properties"
ISO18115_3_NS = "urn:iso:std:iso:18115:-3"

OUTPUT_PATH = Path(__file__).resolve().parent / "output" / "sample.maiml"


def new_uuid() -> str:
    return str(uuidlib.uuid4())


# ---------------------------------------------------------------------------
# 1. maiml_domain でオブジェクトツリーを構築する
# ---------------------------------------------------------------------------

def build_sample_root() -> m.MaimlRootType:
    """maiml_domain のクラスだけを使って、最小構成の MaimlRootType を組み立てる。"""
    vendor = m.VendorType(id="vendor1", content=m.GlobalObjectContent(uuid=m.Uuid(new_uuid())))
    owner = m.OwnerType(id="owner1", content=m.GlobalObjectContent(uuid=m.Uuid(new_uuid())))
    instrument = m.InstrumentType(id="instrument1", content=m.GlobalObjectContent(uuid=m.Uuid(new_uuid())))
    creator = m.CreatorType(
        id="creator1",
        vendor_refs=[m.VendorRefType(id="vref1", ref="vendor1")],
        instrument_refs=[m.InstrumentRefType(id="iref1", ref="instrument1")],
        content=m.GlobalObjectContent(uuid=m.Uuid(new_uuid())),
    )

    doc_decimal_prop = m.DecimalType(
        key="ex:sample-decimal", value=Decimal("1.50"),
        format_string=m.DecimalFormatString("0.00"), units="mm",
    )
    doc_string_prop = m.StringType(key="ex:sample-string", value="hello maiml-domain")

    document = m.DocumentType(
        id="doc1",
        date=datetime.now(timezone.utc),
        creators=[creator],
        vendors=[vendor],
        owners=[owner],
        instruments=[instrument],
        content=m.GlobalObjectContent(
            uuid=m.Uuid(new_uuid()), properties=[doc_decimal_prop, doc_string_prop]
        ),
    )

    place = m.PlaceType(id="place1")
    trans = m.TransitionType(id="trans1")
    arc = m.ArcType(id="arc1", source="place1", target="trans1")
    pnml = m.PnmlType(
        id="pnml1",
        places=[place],
        transitions=[trans],
        arcs=[arc],
        content=m.GlobalObjectContent(uuid=m.Uuid(new_uuid())),
    )

    instruction = m.InstructionType(
        id="instr1",
        transition_refs=[m.TransitionRefType(id="tref1", ref="trans1")],
        content=m.GlobalObjectContent(uuid=m.Uuid(new_uuid())),
    )
    program = m.ProgramType(
        id="program1",
        instructions=[instruction],
        content=m.GlobalObjectContent(uuid=m.Uuid(new_uuid())),
    )
    method = m.MethodType(
        id="method1",
        pnmls=[pnml],
        programs=[program],
        content=m.GlobalObjectContent(uuid=m.Uuid(new_uuid())),
    )
    # ネストした property の例:
    #   <property key="KYL:Cantilever" xsi:type="stringType">
    #     <property key="KYL:ResonanceFrequency" xsi:type="floatType" units="kHz" />
    #     <property key="KYL:ForceConstant" xsi:type="floatType" units="N/m" />
    #   </property>
    # StringType(value=None) が子property(genericDataContainerGroup)だけを持つ
    # ケースで、materialTemplate/material のどちらの子要素としても構築できる
    # ことを確認する。同じ構造をそれぞれ独立したオブジェクトとして作る
    # (親が違うXML要素にまたがって同一オブジェクトを共有することはできないため)。
    def _build_cantilever_property() -> "m.StringType":
        return m.StringType(
            key="KYL:Cantilever",
            properties=[
                m.FloatType(key="KYL:ResonanceFrequency", units="kHz"),
                m.FloatType(key="KYL:ForceConstant", units="N/m"),
            ],
        )

    # ネストした content の例(数値リスト):
    #   <content key="ISO18115-3:Wavenumber" xsi:type="contentDoubleListType"
    #            size="..." units="cm-1" formatString="0.0000" scaleFactor="1"
    #            axis="Wavenumber">
    #     <value>3143.7500 3142.1500 ... </value>
    #   </content>
    # value は xs:list(xs:double) なので、空白区切りの数値列として1つの
    # <value>要素にまとめて出力する。実際の分光データは数百〜数千点になるが、
    # ここでは構造確認用にユーザー提示例の抜粋(15点)のみを使い、size は
    # その抜粋の点数に合わせている(実データでは size=実際の点数になる)。
    _WAVENUMBER_VALUES = [
        3143.7500, 3142.1500, 3140.5500, 3138.9500, 3137.3400, 3135.7400,
        3134.1400, 3132.5300, 3130.9300, 3129.3300, 3127.7200, 3126.1200,
        3124.5100, 3122.9100, 3121.3000,
    ]

    def _build_wavenumber_content() -> "m.ContentDoubleListType":
        return m.ContentDoubleListType(
            key="ISO18115-3:Wavenumber",
            values=list(_WAVENUMBER_VALUES),
            size=len(_WAVENUMBER_VALUES),
            units="cm-1",
            format_string=m.DecimalFormatString("0.0000"),
            scale_factor=1,
            axis="Wavenumber",
        )

    material_template = m.MaterialTemplateType(
        id="material_template1",
        place_refs=[m.PlaceRefType(id="pref1", ref="place1")],
        content=m.GlobalObjectContent(
            uuid=m.Uuid(new_uuid()),
            properties=[_build_cantilever_property()],
            contents=[_build_wavenumber_content()],
        ),
    )
    protocol = m.ProtocolType(
        id="protocol1",
        methods=[method],
        material_templates=[material_template],
        content=m.GlobalObjectContent(uuid=m.Uuid(new_uuid())),
    )

    material = m.MaterialType(
        id="material1", ref="material_template1",
        content=m.GlobalObjectContent(
            uuid=m.Uuid(new_uuid()),
            properties=[_build_cantilever_property()],
            contents=[_build_wavenumber_content()],
        ),
    )
    results = m.ResultsType(
        id="results1", materials=[material],
        content=m.GlobalObjectContent(uuid=m.Uuid(new_uuid())),
    )
    data = m.DataType(
        id="data1", results_list=[results], content=m.GlobalObjectContent(uuid=m.Uuid(new_uuid()))
    )

    # material を data に記録したので、対応する complete イベントを記述する
    # (共通指示書 3.5.5 R-A / EVT-02)。lifecycle:transition="complete" は
    # property として表現し、XES の lifecycle 拡張の正しいURIを
    # <maiml> 要素で xmlns:lifecycle として宣言する(NS-01)。
    complete_prop = m.StringType(key="lifecycle:transition", value="complete")
    event = m.EventType(
        id="event1", ref="instr1",
        content=m.GlobalObjectContent(uuid=m.Uuid(new_uuid()), properties=[complete_prop]),
    )
    trace = m.TraceType(
        id="trace1", ref="program1", events=[event],
        content=m.GlobalObjectContent(uuid=m.Uuid(new_uuid())),
    )
    log = m.LogType(
        id="log1", ref="method1", traces=[trace],
        content=m.GlobalObjectContent(uuid=m.Uuid(new_uuid())),
    )
    event_log = m.EventLogType(
        id="eventlog1", logs=[log], content=m.GlobalObjectContent(uuid=m.Uuid(new_uuid()))
    )

    return m.MaimlRootType(document=document, protocol=protocol, data=data, event_log=event_log)


# ---------------------------------------------------------------------------
# 2. オブジェクトツリーをXMLへ変換する(このファイル限定の最小コンバータ)
# ---------------------------------------------------------------------------

def _sub(parent: ET.Element, tag: str, text=None, **attrs) -> ET.Element:
    el = ET.SubElement(parent, tag)
    for k, v in attrs.items():
        if v is not None:
            el.set(k, str(v))
    if text is not None:
        el.text = str(text)
    return el


_PROPERTY_XSI_TYPES = {
    m.DecimalType: "decimalType",
    m.StringType: "stringType",
    m.FloatType: "floatType",
}

_CONTENT_XSI_TYPES = {
    m.ContentDoubleListType: "contentDoubleListType",
}


def _set_numeric_attrs(el: ET.Element, obj) -> None:
    """formatString/units/scaleFactor は数値系の property/content のみ持つ属性。"""
    if hasattr(obj, "format_string") and obj.format_string is not None:
        el.set("formatString", str(obj.format_string))
    if hasattr(obj, "units") and obj.units is not None:
        el.set("units", obj.units)
    if hasattr(obj, "scale_factor") and obj.scale_factor is not None:
        el.set("scaleFactor", str(obj.scale_factor))


def _add_property(parent: ET.Element, prop) -> None:
    """property要素をXMLへ変換する。property/content配下にさらに
    property/contentがネストしている場合(genericDataContainerGroup)は
    再帰的に処理する。"""
    xsi_type = _PROPERTY_XSI_TYPES[type(prop)]
    p_el = _sub(parent, "property", key=prop.key)
    p_el.set("xsi:type", xsi_type)
    # 出力順序: description -> value -> uncertainty(未対応) -> property* -> content*
    if prop.description is not None:
        _sub(p_el, "description", text=prop.description)
    if prop.value is not None:
        _sub(p_el, "value", text=prop.value)
    for child_prop in prop.properties:
        _add_property(p_el, child_prop)
    for child_content in prop.contents:
        _add_content(p_el, child_content)
    _set_numeric_attrs(p_el, prop)


def _add_content(parent: ET.Element, content_obj) -> None:
    """content要素(数値リスト等)をXMLへ変換する。value は xs:list型
    (空白区切りの数値列)なので、Pythonの values リストを1つの<value>に
    結合して出力する。"""
    xsi_type = _CONTENT_XSI_TYPES[type(content_obj)]
    c_el = _sub(
        parent, "content", key=content_obj.key,
        axis=content_obj.axis, size=content_obj.size,
        id=content_obj.id, ref=content_obj.ref,
    )
    c_el.set("xsi:type", xsi_type)
    # 出力順序: description -> value -> uncertainty(未対応) -> property* -> content*
    if content_obj.description is not None:
        _sub(c_el, "description", text=content_obj.description)
    if content_obj.values:
        _sub(c_el, "value", text=" ".join(str(v) for v in content_obj.values))
    for child_prop in content_obj.properties:
        _add_property(c_el, child_prop)
    for child_content in content_obj.contents:
        _add_content(c_el, child_content)
    _set_numeric_attrs(c_el, content_obj)


def _add_global_content(parent: ET.Element, content: "m.GlobalObjectContent") -> None:
    _sub(parent, "uuid", text=content.uuid)
    for prop in content.properties:
        _add_property(parent, prop)
    for c in content.contents:
        _add_content(parent, c)


def to_xml_string(root_obj: "m.MaimlRootType") -> str:
    """MaimlRootType オブジェクトを整形済みXML文字列に変換する。"""
    document = root_obj.document
    protocol = root_obj.protocol
    data = root_obj.data
    event_log = root_obj.event_log

    maiml_el = ET.Element("maiml")
    maiml_el.set("xmlns", MAIML_NS)
    maiml_el.set("xmlns:xsi", XSI_NS)
    maiml_el.set("xmlns:ex", EX_NS)
    maiml_el.set("xmlns:KYL", KYL_NS)
    maiml_el.set("xmlns:ISO18115-3", ISO18115_3_NS)
    maiml_el.set("xmlns:lifecycle", "http://www.xes-standard.org/lifecycle.xesext#")
    maiml_el.set("xsi:type", "maimlRootType")
    maiml_el.set("version", root_obj.version)

    # --- document ---
    doc_el = _sub(maiml_el, "document", id=document.id)
    _add_global_content(doc_el, document.content)
    for c in document.creators:
        c_el = _sub(doc_el, "creator", id=c.id)
        _add_global_content(c_el, c.content)
        for vr in c.vendor_refs:
            _sub(c_el, "vendorRef", id=vr.id, ref=vr.ref)
        for ir in c.instrument_refs:
            _sub(c_el, "instrumentRef", id=ir.id, ref=ir.ref)
    for v in document.vendors:
        v_el = _sub(doc_el, "vendor", id=v.id)
        _add_global_content(v_el, v.content)
    for o in document.owners:
        o_el = _sub(doc_el, "owner", id=o.id)
        _add_global_content(o_el, o.content)
    for inst in document.instruments:
        inst_el = _sub(doc_el, "instrument", id=inst.id)
        _add_global_content(inst_el, inst.content)
    _sub(doc_el, "date", text=document.date.isoformat())

    # --- protocol ---
    proto_el = _sub(maiml_el, "protocol", id=protocol.id)
    _add_global_content(proto_el, protocol.content)
    for meth in protocol.methods:
        meth_el = _sub(proto_el, "method", id=meth.id)
        _add_global_content(meth_el, meth.content)
        for pn in meth.pnmls:
            pn_el = _sub(meth_el, "pnml", id=pn.id)
            _add_global_content(pn_el, pn.content)
            for pl in pn.places:
                _sub(pn_el, "place", id=pl.id)
            for tr in pn.transitions:
                _sub(pn_el, "transition", id=tr.id)
            for ar in pn.arcs:
                _sub(pn_el, "arc", id=ar.id, source=ar.source, target=ar.target)
        for prog in meth.programs:
            prog_el = _sub(meth_el, "program", id=prog.id)
            _add_global_content(prog_el, prog.content)
            for instr in prog.instructions:
                instr_el = _sub(prog_el, "instruction", id=instr.id)
                _add_global_content(instr_el, instr.content)
                for tref in instr.transition_refs:
                    _sub(instr_el, "transitionRef", id=tref.id, ref=tref.ref)

    for mt in protocol.material_templates:
        mt_el = _sub(proto_el, "materialTemplate", id=mt.id)
        _add_global_content(mt_el, mt.content)
        for pr in mt.place_refs:
            _sub(mt_el, "placeRef", id=pr.id, ref=pr.ref)
        for tr in mt.template_refs:
            _sub(mt_el, "templateRef", id=tr.id, ref=tr.ref)

    # --- data ---
    data_el = _sub(maiml_el, "data", id=data.id)
    _add_global_content(data_el, data.content)
    for res in data.results_list:
        res_el = _sub(data_el, "results", id=res.id)
        _add_global_content(res_el, res.content)
        for mat in res.materials:
            mat_el = _sub(res_el, "material", id=mat.id, ref=mat.ref)
            _add_global_content(mat_el, mat.content)
            for ir in mat.instance_refs:
                _sub(mat_el, "instanceRef", id=ir.id, ref=ir.ref)

    # --- eventLog ---
    elog_el = _sub(maiml_el, "eventLog", id=event_log.id)
    _add_global_content(elog_el, event_log.content)
    for lg in event_log.logs:
        log_el = _sub(elog_el, "log", id=lg.id, ref=lg.ref)
        _add_global_content(log_el, lg.content)
        for tc in lg.traces:
            trace_el = _sub(log_el, "trace", id=tc.id, ref=tc.ref)
            _add_global_content(trace_el, tc.content)
            for ev in tc.events:
                ev_el = _sub(trace_el, "event", id=ev.id, ref=ev.ref)
                _add_global_content(ev_el, ev.content)

    rough = ET.tostring(maiml_el, encoding="unicode")
    pretty = minidom.parseString(rough).toprettyxml(indent="  ")
    pretty = "\n".join(line for line in pretty.split("\n") if line.strip())
    # minidom が付与するXML宣言を、UTF-8明記のものに差し替える
    pretty = pretty.split("\n", 1)[1]
    pretty = '<?xml version="1.0" encoding="UTF-8"?>\n' + pretty
    return pretty


def main() -> None:
    root_obj = build_sample_root()
    print("=== maiml_domain object tree built OK ===")
    print(root_obj)

    xml_text = to_xml_string(root_obj)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(xml_text, encoding="utf-8")
    print(f"=== wrote {OUTPUT_PATH} ===")
    print(
        "MaiML-Schema-1_0 の XSD(および可能であれば JIS K 0200 の業務ルール検証)"
        "にかけて妥当性を確認してください。"
    )


if __name__ == "__main__":
    main()
