# Changelog

このプロジェクトの重要な変更はこのファイルに記録します。
形式は [Keep a Changelog](https://keepachangelog.com/) に、バージョニングは
[Semantic Versioning](https://semver.org/) に準拠します。

MaiML-Library organization の方針により、MaiML仕様(業務ルール・シリアライズ
形式など)に影響する変更は、必ずGitHub Issue/PRでの議論を経てから、このファ
イルへの記載とあわせて行ってください。

## バージョニングポリシー

このリポジトリは `x.y.z` 形式の [Semantic Versioning](https://semver.org/)
に準拠しますが、現在はまだ正式リリース前(`0.y.z`)の段階です。SemVerの
慣習に従い、メジャーバージョン `x` が `0` の間は `x` を固定し、以下の基準で
バージョンを管理します。

- **破壊的変更**(既存クラスの必須引数の追加・変更、フィールド名の変更、
  既存の挙動を変える修正など): `y`(マイナー)を上げる。あわせて
  **GitHub の Release 機能**でリリースノートを作成する。Releaseを作成すると
  リポジトリをWatchしているメンバーに通知が届くため、破壊的変更を能動的に
  知らせる目的も兼ねる。
- **後方互換を保った変更**(機能追加・バグ修正など): `z`(パッチ)を上げる。
  この場合は軽量な `git tag` のみでよく、GitHub Releaseの作成は不要。

`1.0.0` へ上げるタイミング(=正式リリース)は、APIが安定し外部(PyMaiML等の
SDK)からの利用に耐えると判断した時点とします。`1.0.0` 以降は標準的な
SemVerに従い、破壊的変更は `x`(メジャー)、機能追加は `y`(マイナー)、
バグ修正は `z`(パッチ)を上げます。

## [Unreleased]

(このリリース以降の変更をここに追記していきます)

## [0.2.0] - 2026-09-08

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

### Fixed
- `maiml_domain`の全クラス(`@dataclass`のもの・独自`__init__`のものいずれも)
  へ`_StrictAttributesMixin`(`maiml_domain.core`)を追加。未宣言の属性名への
  代入を`AttributeError`で拒否するようになった(**破壊的変更**:
  従来は`results.insertions = [...]`のような、本来`results.content.insertions`
  であるべき代入も無検証で成功し、書き出し側が読まない属性名のため値が
  静かに失われていた。外部レビュー所見10)。宣言済み属性名は
  `@dataclass`なら`dataclasses.fields(cls)`、それ以外は`cls.__mro__`上の
  全`__init__`のパラメータ名の和集合(サブクラスが独自の`__init__`で
  親クラスより狭いシグネチャを持ちつつ`super().__init__(...)`経由で
  親のパラメータ名の属性を設定するケース(例:`PropertyListType`は
  自身の`__init__`に`values`引数を持たないが、`_PropertyListBase.__init__`
  経由で`self.values`を設定する)を誤って弾かないよう、`cls.__init__`単体
  ではなくMRO全体を見る)から自動的に判定するため、既存クラスへの
  個別の追記は不要。アンダースコア始まりの属性名(`HasIdAttributeType`の
  `_id`など、内部実装用)は常に許可する。`copy.deepcopy()`は
  `__setattr__`を経由しない標準の再構築経路のため影響を受けないことを
  確認済み(回帰テストあり)。回帰防止テストを`tests/test_strict_attributes.py`
  に11件追加(このリポジトリ初のpytestテストスイート。開発用依存に
  `pytest`を追加)。

## [0.1.0] - 初期バージョン

- MaiML の各 XSD に対応したドメインクラス一式(`document` / `protocol` / `data` /
  `eventLog` / `pnml` / `core` / `refTypes` / `simpleTypes` / `property`)を実装。
