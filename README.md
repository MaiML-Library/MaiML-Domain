# MaiML-Domain

[![Tests](https://github.com/MaiML-Library/MaiML-Domain/actions/workflows/test.yml/badge.svg)](https://github.com/MaiML-Library/MaiML-Domain/actions/workflows/test.yml)

MaiML(JIS K 0200 / MaiML-Schema-1_0)の XSD 定義に対応した Python ドメインモデルライブラリです。
[MaiML-Library](https://github.com/MaiML-Library) organization におけるSDK
([PyMaiML](https://github.com/MaiML-Library/PyMaiML) など)や周辺ツールが共通して利用する、
基盤となる共通データモデルです。

## 特徴

- MaiML の各 XSD(`maiml-core.xsd` / `maiml-property.xsd` / `maiml-document.xsd` / `maiml-protocol.xsd` /
  `maiml-data.xsd` / `maiml-eventLog.xsd` / `maiml-pnml.xsd` / `maiml-refTypes.xsd` / `maiml-simpleTypes.xsd` /
  `maiml.xsd`)に 1:1 で対応したドメインクラスを提供します。
- property/content 型はスカラー型 23 種・property 側リスト型 23 種(`PropertyListType` 含む)・content 側リスト型 22 種を完全に網羅しています。
- 暗号化されたプロパティ/コンテンツ(`encryptionGroup`)用の `EncryptionType` にも対応しています(平文フィールドとの排他はコンストラクタで検証します)。
- 依存ライブラリなし(Python 標準ライブラリのみ)。

## インストール

開発版をローカルからインストールする場合:

```bash
git clone https://github.com/MaiML-Library/MaiML-Domain.git
cd MaiML-Domain
pip install -e .
```

## 使い方

```python
from datetime import datetime
from maiml_domain import (
    DocumentType, VendorType, OwnerType, CreatorType, VendorRefType,
)

vendor = VendorType(id="v1")
owner = OwnerType(id="o1")
creator = CreatorType(id="c1", vendor_refs=[VendorRefType(id="vr1", ref="v1")])

document = DocumentType(
    id="d1",
    date=datetime.now(),
    creators=[creator],
    vendors=[vendor],
    owners=[owner],
)
```

パッケージ内モジュールと対応 XSD・主なクラスの詳細な一覧は
[`maiml_domain/README.md`](./maiml_domain/README.md) を参照してください。

## MaiML-Library における位置づけ

MaiML-Library organization は次のような階層構造を基本方針としています([`.github`](https://github.com/MaiML-Library/.github) の組織方針を参照)。

- **MaiML-Domain**(本リポジトリ) -- JIS K 0200 / MaiML XSDに対応する、
  言語SDK共通のドメインモデル。MaiMLの構造・型・ローカル制約を表現する。
  Pythonでの実装
- **PyMaiML**([MaiML-Library/PyMaiML](https://github.com/MaiML-Library/PyMaiML)) --
  MaiML-Domainを基盤として、MaiML文書の読み書き、検証、検索、構築、
  意味的操作を提供するPython SDK。他言語向けSDKを追加する場合、本
  リポジトリはPython実装のため直接は共有できず、その言語向けに本
  リポジトリ相当のドメインモデルを別途実装することになる
- API・ツール群 -- SDK / ドメイン層に依存

## バリデーションの範囲

本リポジトリは「純粋なデータモデル」を掲げていますが、完全に無検証というわけではありません。
責務境界の基準は次の一文です(`MaiML_Domain_XSD_builtin_validation_policy.md`で確定した方針)。

> **MaiML-Domainは、単一のDomainフィールドまたは単一オブジェクトのみから判定でき、
> XML namespace contextや他オブジェクトとの関係を必要としない制約を検証する。**
> namespaceの解決、idの文書内一意性、IDREFの参照先解決、その他のオブジェクト間・
> セクション間の整合性検証はPyMaiMLが担う。

「単一フィールドのみ」ではなく「単一オブジェクト」まで含めているのは、`encryption`と
平文フィールドの`xs:choice`排他検証のように、同一オブジェクト内の複数フィールドを
見る必要はあるが文書全体のコンテキストは不要な検証を含めるためです。

対象の具体例(`minOccurs`/`maxOccurs`、`xs:choice`の排他性、required属性、`simpleType`の
うち対応している字句・値域制約など)は各クラスのコンストラクタで検証し、違反時には
`ValueError`/`TypeError`を送出します(例: `HasIdAttributeType.id`が空文字またはNCNameとして
不正なら拒否、`GlobalObjectContent`で`encryption`と平文フィールドを同時に指定すると拒否、
integer系の値域超過・UUID字句不正・xs:decimalの非有限値(NaN/Infinity)を拒否、`xs:ID`/
`xs:IDREF`のNCName字句制約、`xs:QName`のプレフィックス:ローカル名構文、`xs:language`の
パターンなど)。`xs:QName`の字句検証は`QualifiedNameType`だけでなく、全property/content
共通の`UncertaintyBaseType.key`属性(これ自体もxs:QName)にも適用しています。

もう一つの原則として、**MaiML-DomainはXML上の元の字句表現ではなく、XSDの値空間に対応する
Python値を表現します**(例: `xs:dateTime` → `datetime`、`xs:decimal` → `Decimal`/`int`、
`xs:base64Binary` → `bytes`)。したがって元XMLの文字列表現を完全に保存・再現することは
目的としていません。

### XSD built-in型ごとの責務

| XSD型 | MaiML-Domain | PyMaiML / XML層 |
|---|---|---|
| `xs:string` / `xs:boolean` | Python型検証 | ― |
| `xs:decimal` / integer系 | 型・値域・有限性検証 | ― |
| `xs:ID` | NCName字句制約 | 文書内一意性 |
| `xs:IDREF` | NCName字句制約 | 参照先の存在・型チェック |
| `xs:QName` | QName字句・構文(prefix:localのNCName構成) | prefix → namespace URI解決 |
| `xs:language` | XSDのパターン facet(構文) | 言語サブタグレジストリ等を使う意味検証 |
| `xs:token` | 現状維持(下記参照) | whitespace正規化を別途検討 |
| `xs:anyURI` | 過剰検証しない(下記参照) | 到達性・外部リソース確認等 |
| `xs:dateTime` / `xs:base64Binary` / `xs:hexBinary` | Python型(`datetime`/`bytes`)への変換 | XML lexical formの処理 |

`xs:token`のwhiteSpace collapseは「拒否のための検証」というより値の正規化であり、
コンストラクタで入力値を暗黙に書き換えると「渡した値がそのまま保持される」という直感を
崩しかねないため、現時点では積極的な正規化をDomainへ導入していません。`xs:anyURI`も
`urn:example:data`や相対パスなど多様な形式を許容するため、HTTP(S)スキームや到達可能性を
要求する専用バリデータとしては扱いません。いずれも必要性を確認したうえで別Issueとして
検討する対象です。

一方、**複数要素・複数セクションをまたいで初めて判断できる検証**(`id`/`ref`の整合性、
`ref`参照先の型チェック、イベントログの`lifecycle:transition="complete"`必須化など
JIS / MaiML AI Common Specificationの業務ルール)は、あえて本リポジトリの責務外としています。
これらはSDK層([PyMaiML](https://github.com/MaiML-Library/PyMaiML)の`pymaiml.validation`)
が担います。新しい検証ロジックをどちらに実装すべきか迷ったら、この基準(単一フィールド/
単一オブジェクトだけで判定できるか否か)に照らして判断してください。

## コントリビューション

仕様に関わる変更は Issue / Pull Request で議論のうえ、[`CHANGELOG.md`](./CHANGELOG.md) に記録してください。
バグ報告・ドキュメント改善なども歓迎します。詳しい手順(XSD更新時の対応・
`_StrictAttributesMixin`の規約・バリデーションの範囲など)は
[`CONTRIBUTING.md`](./CONTRIBUTING.md) を参照してください。

## ライセンス

Apache License 2.0 ([LICENSE](./LICENSE) を参照)
