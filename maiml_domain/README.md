# maiml_domain

`maiml_domain` は、MaiML の各 XSD
定義に対応したドメインモデルを提供するパッケージである。\
各モジュールは XSD ごとに分割され、スキーマ構造と 1:1
に近い形でクラスを定義している。

------------------------------------------------------------------------

## 📦 パッケージ構成

    maiml_domain/
    ├── simple_types.py
    ├── core.py
    ├── property.py
    ├── ref_types.py
    ├── document.py
    ├── pnml.py
    ├── protocol.py
    ├── data.py
    ├── event_log.py
    └── root.py

------------------------------------------------------------------------

## 🗂 モジュール一覧

  -------------------------------------------------------------------------------------
  ファイル               対応XSD                   主なクラス
  ---------------------- ------------------------- ------------------------------------
  `simple_types.py`      `maiml-simpleTypes.xsd`   Uuid, IsoLanguageName,
                                                   DecimalFormatString,
                                                   FloatFormatString,
                                                   IntegerFormatString

  `core.py`              `maiml-core.xsd`          HashType, InsertionType,
                                                   HasIdAttributeType,
                                                   GlobalObjectContent,
                                                   SimpleObjectType,
                                                   ReferenceObjectType,
                                                   TripleObjectType

  `property.py`          `maiml-property.xsd`      UncertaintyBaseType,
                                                   PropertyBaseType, ContentBaseType +
                                                   スカラー型23種 +
                                                   リスト型（property/content）各24種

  `ref_types.py`         `maiml-refTypes.xsd`      CreatorRefType, VendorRefType,
                                                   OwnerRefType, InstrumentRefType,
                                                   PlaceRefType, TransitionRefType,
                                                   ResultsRefType, TemplateRefType,
                                                   InstanceRefType

  `document.py`          `maiml-document.xsd`      DocumentType, CreatorType,
                                                   VendorType, OwnerType,
                                                   InstrumentType, ChainType,
                                                   ParentType

  `pnml.py`              `maiml-pnml.xsd`          PnmlType, PlaceType, TransitionType,
                                                   ArcType

  `protocol.py`          `maiml-protocol.xsd`      ProtocolType, MethodType,
                                                   ProgramType, InstructionType,
                                                   MaterialTemplateType,
                                                   ConditionTemplateType,
                                                   ResultTemplateType

  `data.py`              `maiml-data.xsd`          DataType, ResultsType, MaterialType,
                                                   ConditionType, ResultType

  `event_log.py`         `maiml-eventLog.xsd`      EventLogType, LogType, TraceType,
                                                   EventType, ExtensionType,
                                                   GlobalsType, ClassifierType,
                                                   AttributableType

  `root.py`              `maiml.xsd`               RootObjectType, MaimlRootType,
                                                   ProtocolFileRootType
  -------------------------------------------------------------------------------------

------------------------------------------------------------------------

## 🧠 設計方針

-   XSD単位でモジュール分割
-   スキーマ構造とドメインモデルの対応を明確化
-   型安全性と拡張性を優先
-   参照型（RefType）を独立管理
-   PNML構造を独立モジュール化

------------------------------------------------------------------------

## 🔗 依存関係（概略）

    root
     ├── document
     ├── protocol
     │     └── pnml
     ├── data
     ├── event_log
     └── core
           ├── simple_types
           ├── property
           └── ref_types

------------------------------------------------------------------------

## 🎯 目的

-   MaiML XML の構造を Python ドメインモデルとして表現
-   XML ⇄ オブジェクト変換の基盤
-   将来的なバリデーション・変換・エディタ機能の基礎レイヤ
