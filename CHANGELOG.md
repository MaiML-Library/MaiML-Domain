# Changelog

このプロジェクトの重要な変更はこのファイルに記録します。

## [Unreleased]

### Added
- `EncryptionType`(`maiml_domain.core`)を追加し、`globalObjectContentGroup` および
  全 property/content 型が持つ `encryptionGroup`(暗号化コンテンツの選択肢)をサポート。
- `GlobalObjectContent` と property/content 型の共通基底(`UncertaintyBaseType`)に
  `encryption` フィールドを追加。平文フィールド(value/description/uncertainty/property/content)
  との同時指定は `ValueError` になる(XSD の `xs:choice` に対応)。

### Changed
- スカラー型 23 種(`StringType` 〜 `LanguageType`)を `_ScalarPropertyBase` /
  `_NumericScalarPropertyBase` の共通基底クラスに整理し、重複コードを削減
  (`property.py`: 840 行 → 522 行)。
- `DateTimeFormatString` のバリデーションを、`maiml-simpleTypes.xsd` の
  `dateTimeFormatStringType` パターン(`YYYY-MM-DDThh:mm:ss(\.s+)?(TZD)?` という
  リテラルプレースホルダ表記)に忠実な実装に修正。従来はマッチしない値も
  無検証で受理されていた。

### Removed
- 未使用のデッドコード(`_make_property_type` / `_make_content_type` / `_common_fields`)
  を `property.py` から削除。
- `simple_types.py` の未使用・誤エスケープだった `DecimalFormatString._PATTERN`、
  未使用 import(`NewType`)を削除。
- リポジトリ内の `.DS_Store` / `__pycache__` / 未完成の DDD スキャフォールド
  (`maiml_domain/maiml/` 以下)を整理。

## [0.1.0] - 初期バージョン

- MaiML の各 XSD に対応したドメインクラス一式(`document` / `protocol` / `data` /
  `eventLog` / `pnml` / `core` / `refTypes` / `simpleTypes` / `property`)を実装。
