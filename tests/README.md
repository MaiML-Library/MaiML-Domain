# tests/

`build_sample_maiml.py` は、`maiml_domain` のクラスだけを使って最小構成の
`MaimlRootType` オブジェクトツリーを組み立て、それを MaiML-Schema-1_0 準拠の
XMLとして書き出す検証スクリプトです。

`maiml_domain` にはまだ `to_xml()` のような正式なシリアライズ機能が無いため、
このスクリプト内に最小限のXMLコンバータを直接実装しています(ライブラリ本体
のAPIではありません)。

## 実行方法

```bash
pip install -e .
python3 tests/build_sample_maiml.py
```

`tests/output/sample.maiml` が生成されます(このディレクトリは `.gitignore`
対象です)。生成したファイルは、MaiML-Schema-1_0 の公式XSD、および可能であれば
JIS K 0200 の業務ルール検証(id/refの整合性・出力順序・UUID形式など)にかけて
妥当性を確認してください。

## 動作確認済みの内容

- document / creator / vendor / owner / instrument / protocol / method /
  pnml (place / transition / arc) / program / instruction / materialTemplate /
  data / results / material / eventLog / log / trace / event の一連の構造。
- creator から `vendorRef` / `instrumentRef` による参照(id/ref)を含めて
  出力できることを確認。
- `materialTemplate`(`placeRef` で `place` を参照)と、それを `ref` で参照する
  `material` の組を1つずつ構築し、id/refの整合性を含めて確認。
- `material` を `data` に記録したことで発生する EVT-02
  (計測結果を記録したら対応する `lifecycle:transition="complete"` の
  `<event>` が必須になるルール)についても、既存の `event1`
  (`instr1` を参照)に `lifecycle:transition` プロパティを追加し、
  `<maiml>` 要素で `xmlns:lifecycle` を XES 標準の正しいURIで宣言することで
  対応済み。
- document 直下に `property`(`DecimalType` / `StringType`)を1つずつ含め、
  `xsi:type` / `key` / `formatString` / `units` の出力を確認。
- **ネストした `property`**(`property` の子要素としてさらに `property` を
  持つケース、`genericDataContainerGroup`)を `materialTemplate` と
  `material` の両方の子要素として構築し、確認。例:
  `StringType`(値なし)の下に `FloatType` を2つぶら下げる構造
  (`KYL:Cantilever` → `KYL:ResonanceFrequency` / `KYL:ForceConstant`)。
  独自の `key` プレフィックスを使う場合は、`<maiml>` 要素で対応する
  `xmlns:` 宣言が必須である点(XSD-01, xs:QName検証)も確認できた。
- **`content`(数値リスト)**を `materialTemplate` と `material` の両方の
  子要素として構築し、確認。例: `ContentDoubleListType`
  (`ISO18115-3:Wavenumber`、`axis`/`size`/`units`/`formatString`/
  `scaleFactor` 付き)。`value` は `xs:list(xs:double)` 型なので、Python側の
  `values`(数値のリスト)を空白区切りの文字列にまとめて1つの `<value>` として
  出力する変換ロジックを実装。`_add_property`/`_add_content` は相互に再帰
  呼び出しできるようにし、`property`/`content` のどちらの側からもネスト可能
  なことを確認済み。
- 上記構成で MaiML-Schema-1_0 の検証(MUSTレベル)がエラー0件で通ることを
  確認済み(SHOULDレベルの参考情報として、creator/vendor/owner/instrument
  のUUIDに名前ベースのv3/v5を推奨する旨の指摘のみ)。

## 今回のテストで対象外にしたもの

- `EncryptionType`(暗号化コンテンツ)のXML出力。Pythonオブジェクトとしての
  相互排他バリデーションは別途確認済みですが、`xenc:EncryptedData` の実際の
  XML構造までは作り込んでいません。
- `condition` / `resultTemplate` / `result`(material と同型の構造)。
  仕組みは material と同じなので、必要になった際に同じパターンで追加できます。
- `instanceRef`(material/condition/result からテンプレートの個々の
  インスタンスへの参照)。
- `property`/`content` の `uncertainty` 子要素のXML出力。
- `contentDoubleListType` 以外の `content` 型(`contentStringListType` 等)。
  仕組みは `contentDoubleListType` と同じなので、必要になった際に同じ
  パターンで追加できます。
- `content` の `id`/`ref` 属性(他の `content` からの参照)。
