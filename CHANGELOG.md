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

- **`CONTRIBUTING.md`を追加しました。** [PyMaiML](https://github.com/MaiML-Library/PyMaiML)の
  `CONTRIBUTING.md`を土台に、本リポジトリの実際の性質(XSDを同梱しない、
  シリアライズ処理を持たない、実行時依存パッケージがゼロ)に合わせて
  書き直しています。MaiML-Schema-1_0が更新された際のクラス追加・修正の
  手順、新規クラスに`_StrictAttributesMixin`を必ず継承させる規約
  (外部レビュー所見10に基づく既存の修正を、今後のコントリビューションにも
  明文化したもの)、README.mdの「バリデーションの範囲」の原則をコンストラクタ
  実装時の判断基準として再掲したもの、PyPI公開順序(本リポジトリが
  SDK群より先)についての短い節、`DocumentType.signature`をあえて生の文字列
  のまま保持している設計意図とSignatureの扱い(署名の生成・検証は外部の
  署名ツールで行う)の節を含みます。README.mdの「コントリビューション」
  節から新しい`CONTRIBUTING.md`へリンクを追加しました。
- **署名済みMaiMLファイルの保存に関するルールを`CONTRIBUTING.md`の
  「Signature(電子署名)の扱い」節に追記しました。** 署名済みMaiMLを保存
  する際は、XMLの再整形・コメント削除・空白削除など、署名対象XMLの
  正準化結果を変化させる処理を行ってはならないというルールです
  ([PyMaiML](https://github.com/MaiML-Library/PyMaiML)のCONTRIBUTING.mdに
  追記した同ルールへのポインタです)。コード変更はありません。
- **署名済みMaiMLの保存ルールを、MaiML-Signer(外部の署名ツール)の
  README記載内容を踏まえて拡充しました。** 改行コード(CRLF/LF)の変換や
  属性の並び替えも正準化結果に影響することを`CONTRIBUTING.md`に追記
  しています(詳細はPyMaiML側のCONTRIBUTING.mdを参照)。コード変更は
  ありません。

- **外部レビュー(`MaiML_Domain_PyMaiML_required_fixes.md`)で指摘された、
  `property.py`のスカラー`value`/リスト`values`要素に対する字句検証の
  欠落を修正しました。** 【高】`IntType(value="not-an-int")`や
  `BooleanType(value="yes")`のような型不正な値が、これまでは無検証で
  構築できてしまっていました。各スカラー/リスト型に`_value_types`
  (許容するPython型)を宣言する仕組みを追加し、UncertaintyBaseTypeの
  `_check_value()`で一括検証するようにしました。整数系(`IntType`/
  `LongType`/`ShortType`/`ByteType`/`UnsignedInt`/`UnsignedLong`/
  `UnsignedShort`/`UnsignedByteType`)は`bool`を明示的に拒否した上で
  xs:byte〜xs:unsignedLongそれぞれのXSD字句範囲(例:
  xs:byte は -128〜127)も検証します。`UuidType`はUUIDの正規表現パターン
  (`simple_types.UUID_PATTERN`)も検証します。`DecimalType`は`Decimal`と
  `int`(xs:decimalの字句空間に整数も含まれるため)を受け付けます。
- **同レビューで指摘された、`properties`/`contents`/`uncertainties`
  リスト属性の要素型検証の欠落も修正しました。** 【高】
  `properties=[object()]`のような不正な要素を含むリストが、これまでは
  無検証で構築できてしまっていました。`maiml-property.xsd`の
  `property`/`content`/`uncertainty`要素の型宣言
  (`propertyBaseType`/`contentBaseType`/`uncertaintyBaseType`)どおりに、
  各要素が`PropertyBaseType`/`ContentBaseType`/`UncertaintyBaseType`の
  インスタンスであることを構築時に検証する`_check_list_element_types()`
  を追加し、`_ScalarPropertyBase`/`_PropertyListBase`/`_ContentListBase`
  の3箇所から呼び出しています。
- **`ContentBaseType.id`/`ref`の空文字許容を、`HasIdAttributeType.id`と
  同じ拒否に統一しました。** 【中】どちらも`maiml-property.xsd`/
  `maiml-helper.xsd`上は`xs:ID`/`xs:IDREF`(xs:NCName由来、空文字を
  許容しない)ですが、`ContentBaseType`側だけ検証が抜けていました。
- **`property.py`の3箇所(`_ScalarPropertyBase`/`_PropertyListBase`/
  `_ContentListBase`)に重複していた`encryption`と平文フィールドの
  排他チェックを、共通ヘルパー`_check_encryption_exclusive()`へ
  抽出しました。** 【中】保守性向上のリファクタリングで、挙動は
  変わりません。
- **README.md / `maiml_domain/README.md`を現行実装に合わせて更新しました。**
  【低】`simple_types.py`のクラス一覧に`DateTimeFormatString`が、
  `core.py`のクラス一覧に`EncryptionType`が、それぞれ抜けていたのを
  追加しました。`property.py`のリスト型数の記載
  (誤:「リスト型(property/content)各24種」)を実際の内訳
  (property側23種・content側22種)に修正しました。

- **`MaiML_Domain_new_required_fixes.md`(前回修正のレビュー)で指摘
  された、`DecimalType`/`DecimalListType`/`ContentDecimalListType`が
  非有限値を拒否しない問題を修正しました。** 【高】`xs:decimal`は
  `xs:float`/`xs:double`と異なりNaN/Infinity/-Infinityを値空間に含まない
  ため、`Decimal("NaN")`のような値は本来Domainオブジェクトとして構築
  できてはならない。`_check_value_extra()`に`Decimal.is_finite()`に
  よるチェックを追加した(`int`は常に有限なので対象外)。
- **前回修正で追加した検証(スカラー`value`の型検証、integer系値域検証、
  UUID字句検証、`properties`/`contents`/`uncertainties`要素型検証、
  `ContentBaseType.id`/`ref`空文字拒否、encryption/平文排他チェック)に
  対する専用回帰テストを追加しました。** 【高】これまでは
  `tests/build_sample_maiml.py`による正常系の疎通確認のみで、上記の
  検証ロジックを直接固定するテストが無く、将来の`property.py`
  リファクタリングで検証が意図せず失われても気付けない状態だった。
  `tests/test_property_validation.py`(新規)へ33件のテストを追加
  (本項目のDecimal非有限値チェックを含む)。
- **README.mdの「バリデーションの範囲」の記載を、現在の実装範囲に
  合わせて調整しました。** 【中〜低】旧文言は「`simpleType`の字句上の
  制約など」を検証すると読め、全simpleTypeの字句制約を完全に保証して
  いるように誤解されかねなかった。実際には`xs:ID`/`xs:IDREF`の
  NCName字句制約・`xs:QName`・`xs:language`などはPython型の確認に
  留まっている旨を明記し、対応範囲を広げる場合は別Issueとして切り出す
  ことを推奨する一文を追加した。

- **`MaiML_Domain_XSD_builtin_validation_policy.md`に基づき、
  MaiML-Domain/PyMaiMLの検証責務境界を明文化し、`xs:ID`/`xs:IDREF`/
  `xs:QName`/`xs:language`のローカルな字句検証を追加しました。**
  責務境界を「単一のDomainフィールドまたは単一オブジェクトのみから
  判定でき、XML namespace contextや他オブジェクトとの関係を必要と
  しない制約」と確定し、README.mdの「バリデーションの範囲」へXSD
  built-in型ごとの責務表とともに反映、CONTRIBUTING.mdの該当節からも
  参照するようにしました。あわせて以下のローカル字句検証を実装:
  - `xs:ID`/`xs:IDREF`: NCName字句制約(`IdType`/`IdRefType`/
    `IdRefListType`/`ContentIdRefListType`、および
    `HasIdAttributeType.id`/`ContentBaseType.id`/`ref`)。文書内一意性・
    参照先解決は引き続きPyMaiMLの責務。
  - `xs:QName`: prefix:localの構文チェック(各部がNCName、コロンは
    高々1つ)を`QualifiedNameType`/`QualifiedNameListType`/
    `ContentQualifiedNameListType`へ追加。prefix→namespace URI解決は
    引き続きPyMaiMLの責務(MaiML-Domainへnamespace管理を持ち込まない)。
  - `xs:language`: XSD自体のパターンfacet(`[a-zA-Z]{1,8}(-[a-zA-Z0-9]
    {1,8})*`)による構文チェックを`LanguageType`/`LanguageListType`/
    `ContentLanguageListType`へ追加。実在する言語コードかの意味検証は
    対象外。

  各項目に対する正常系・異常系の回帰テストを`tests/test_property_
  validation.py`へ25件追加しました。`xs:token`のwhiteSpace正規化と
  `xs:anyURI`は、ポリシー文書の推奨どおり必要性を確認してから別途
  検討する対象として今回は対応していません。

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
