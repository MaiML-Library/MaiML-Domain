# MaiML-Domain

MaiML(JIS K 0200 / MaiML-Schema-1_0)の XSD 定義に対応した Python ドメインモデルライブラリです。
[MaiML-Library](https://github.com/MaiML-Library) organization におけるSDK
([PyMaiML](https://github.com/MaiML-Library/PyMaiML) など)や周辺ツールが共通して利用する、
基盤となる共通データモデルです。

## 特徴

- MaiML の各 XSD(`maiml-core.xsd` / `maiml-property.xsd` / `maiml-document.xsd` / `maiml-protocol.xsd` /
  `maiml-data.xsd` / `maiml-eventLog.xsd` / `maiml-pnml.xsd` / `maiml-refTypes.xsd` / `maiml-simpleTypes.xsd` /
  `maiml.xsd`)に 1:1 で対応したドメインクラスを提供します。
- property/content 型はスカラー型 23 種・リスト型 23 種(base 含む)・コンテンツリスト型 22 種を完全に網羅しています。
- 暗号化されたプロパティ/コンテンツ(`encryptionGroup`)にも対応しています。
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

- **MaiML-Domain**(本リポジトリ) -- 共通データモデル(基盤)
- 言語別 SDK(例: [PyMaiML](https://github.com/MaiML-Library/PyMaiML)) -- 本リポジトリを利用して構築
- API・ツール群 -- SDK / ドメイン層に依存

## バリデーションの範囲

本リポジトリは「純粋なデータモデル」を掲げていますが、完全に無検証というわけではありません。
**XSD単体(1つのcomplexType定義)を見るだけで機械的に判断できる制約**
(`minOccurs`/`maxOccurs`、`xs:choice`の排他性、required属性、`simpleType`の字句上の制約など)は
各クラスのコンストラクタで検証し、違反時には`ValueError`/`TypeError`を送出します
(例: `HasIdAttributeType.id`が空文字なら拒否、`GlobalObjectContent`で`encryption`と
平文フィールドを同時に指定すると拒否、など)。一方、**複数要素・複数セクションをまたいで
初めて判断できる検証**(`id`/`ref`の整合性、`ref`参照先の型チェック、イベントログの
`lifecycle:transition="complete"`必須化などJIS / MaiML AI Common Specificationの業務ルール)は、
あえて本リポジトリの責務外としています。これらはSDK層
([PyMaiML](https://github.com/MaiML-Library/PyMaiML)の`pymaiml.validation`)が担います。
新しい検証ロジックをどちらに実装すべきか迷ったら、この基準(1つのcomplexType定義だけで
判定できるか否か)に照らして判断してください。

## コントリビューション

仕様に関わる変更は Issue / Pull Request で議論のうえ、[`CHANGELOG.md`](./CHANGELOG.md) に記録してください。
バグ報告・ドキュメント改善なども歓迎します。

## ライセンス

Apache License 2.0 ([LICENSE](./LICENSE) を参照)
