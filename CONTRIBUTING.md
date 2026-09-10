# Contributing

MaiML仕様(業務ルール・データモデルの構造など)に影響する変更は、必ず
GitHub Issue/PRでの議論を経てから行い、`CHANGELOG.md`に記載してください。
組織全体の方針は
[MaiML-Library/.github](https://github.com/MaiML-Library/.github/blob/main/profile/README.md)
を参照してください。バージョンの上げ方(破壊的変更か後方互換かの判断・
GitHub Releaseの要否)は`CHANGELOG.md`冒頭の「バージョニングポリシー」に
従ってください(本ファイルでは繰り返しません)。

## MaiML-Schema-1_0が更新されたときの手順

本リポジトリは[PyMaiML](https://github.com/MaiML-Library/PyMaiML)と違い、
XSDファイル自体を同梱していません(XMLの読み書き・スキーマ検証は行わない
「純粋なデータモデル」であるため)。そのため更新手順もPyMaiML側の
チェックリストとは性格が異なり、「新しい/変更されたXSDのcomplexTypeを、
1つずつPythonクラスへ機械的に翻訳する」作業が中心になります。

1. **どのモジュールに属するクラスかを判断する。** `maiml_domain/`は
   XSDファイル(またはXSDが定義する層)ごとにモジュールを分けています
   (`simple_types.py`/`core.py`/`property.py`/`ref_types.py`/
   `document.py`/`pnml.py`/`protocol.py`/`data.py`/`event_log.py`/
   `root.py`、対応関係の詳細は`maiml_domain/README.md`の一覧表を参照)。
   新規complexTypeがどの層に属するかをまず特定してください。

2. **クラスを追加・修正する。** `xs:sequence`の子要素の出現順序・
   出現数(`minOccurs`/`maxOccurs`)、`xs:choice`の排他性、必須属性を、
   コンストラクタの引数(型・`Optional`か否か・デフォルト値の有無)へ
   そのまま反映してください。既存クラスと同様、`@dataclass`または
   カスタム`__init__`のどちらの形にするかは、同じモジュール内の既存
   クラスの書き方に合わせるのが基本です。

3. **`_StrictAttributesMixin`を必ず継承させる。** 新しいクラスは
   (`@dataclass`・カスタム`__init__`のどちらであっても)必ず
   `core.py`の`_StrictAttributesMixin`を基底クラスに含めてください。
   これは宣言していない属性名への代入を`AttributeError`で拒否する
   ためのもので、外部レビューで発見された「`results.insertions = [...]`
   (正しくは`results.content.insertions`)のような属性名の書き間違いが、
   例外も出さずにそのまま握りつぶされていた」という実際の不具合の再発
   防止策です(詳細は`core.py`内のクラスdocstring、および
   `tests/test_strict_attributes.py`のモジュールdocstringを参照)。
   `@dataclass`ならフィールド定義から、カスタム`__init__`なら
   `self.<param_name> = <param_name>`という命名規則から、宣言済み属性名を
   自動的に検出する仕組みになっているため、この規則さえ守れば追加の
   ボイラープレートは不要です。

4. **コンストラクタでの検証は「単体のcomplexTypeだけで判断できる範囲」に
   留める。** README.mdの「バリデーションの範囲」で説明している通り、
   `minOccurs`/`maxOccurs`、`xs:choice`の排他性、required属性、
   `simpleType`の字句上の制約など、**そのcomplexType定義だけを見れば
   機械的に判断できる制約**はコンストラクタで検証し、違反時に
   `ValueError`/`TypeError`を送出してください(既存の`HashType.value`が
   `bytes`でなければ`TypeError`、`InsertionType.uri`が空文字なら
   `ValueError`、といった例と同じパターンです)。逆に、`id`/`ref`の
   整合性やイベントログの`lifecycle:transition="complete"`必須化のような
   **複数要素・複数セクションをまたいで初めて判断できる検証**は、
   意図的に本リポジトリの責務外としてください。これは
   [PyMaiML](https://github.com/MaiML-Library/PyMaiML)の
   `pymaiml.validation`が担う領域です。どちらに実装すべきか迷う場合は、
   この基準(1つのcomplexType定義だけで判定できるか否か)で判断してください。

5. **テストを追加する。** 新しいクラスの正常系(妥当な値でインスタンス
   化できる)・異常系(手順4で追加した検証が正しく`ValueError`/
   `TypeError`を送出する)・`_StrictAttributesMixin`により未宣言の属性名
   への代入が`AttributeError`になることの3点は、最低限テストで確認して
   ください。

6. **`CHANGELOG.md`に記載し、バージョンを上げる。** 既存クラスの必須
   引数の追加・変更やフィールド名の変更などは破壊的変更として扱い、
   `CHANGELOG.md`冒頭のバージョニングポリシーに従ってください。

## SDK側との関係(PyMaiML等)

本リポジトリはMaiML-Libraryの各言語SDK(現状は[PyMaiML](https://github.com/MaiML-Library/PyMaiML))が
直接利用する基盤であり、`pyproject.toml`に見ての通り実行時の依存パッケージを
一切持ちません。そのため、PyPI公開の順序は次のようになります。

1. 本リポジトリを先にPyPIへ公開(またはGitHubタグをリリース)する。
2. 下流のSDK(PyMaiML等)側が、公開されたバージョンに対する範囲指定
   (例: `maiml-domain>=0.2,<0.3`)へ依存を切り替える。

本リポジトリの破壊的変更(`CHANGELOG.md`のバージョニングポリシーに従って
マイナー`y`を上げる変更)は、そのままSDK側にとっても追従が必要な変更に
なるため、GitHub Releaseの作成(通知)は特に重要です。

## Signature(電子署名)の扱い

`maiml_domain.document.DocumentType`は`<Signature>`要素を`signature`
フィールド(`Optional[str]`)として保持しますが、構造化されたクラスとして
モデル化はしていません(生のXML文字列のまま保持するだけです)。これは
意図的な設計です。

- MaiMLの`<Signature>`は、JIS X 5093 / ETSI TS 101 903(XAdES)準拠の
  enveloped署名として扱うべきもので、Digestは署名時点の厳密なバイト列に
  対して計算されます。本リポジトリはXMLのシリアライズ(バイト列の生成・
  読み込み)自体を担当しないため、署名の生成・検証(暗号学的な妥当性の
  確認)はそもそも本リポジトリの責務の範囲外です。
- 署名の生成・検証は、外部の署名ツールを使って、シリアライズ済みの
  バイト列(例: PyMaiMLの`dumps()`/`dump()`が出力したもの)に対して
  直接行ってください。
- 将来的に構造化した`Signature`型のサポートを検討する場合も、上記の
  「バリデーションの範囲」の原則(単体のcomplexTypeとして判断できる
  構造上の制約のみをここで扱い、署名の暗号学的な妥当性の検証は含めない)
  に従ってください。
