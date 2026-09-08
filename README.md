# loop-data-source — itonami データソース事業の統括 charter repo

**名乗り:** `loop-data-source` は役割面（role plane, ADR-2608040100）の repo 名です。
この repo が所有するのは **itonami のデータソース事業** —— 公開ライセンスの研究データ
（SEC market-intel / GLEIF LEI）を収集・正規化して kotobase.net x402 で販売する
corpus を束ねる統括（charter/coordinator）です。実働の bot は Hermes profile
`data-source-market-intel` と `data-source-gleif` の 2 体で、この repo は両者の
管轄・境界・配信契約を宣言する場所です。

## 事業の対象

- **market-intel**: SEC 公開ファイリング（公開ライセンス）から company 情報を
  収集・正規化する corpus bot（`data-source-market-intel`）。
- **gleif**: GLEIF が公開する LEI（Legal Entity Identifier）カタログを収集・
  正規化する corpus bot（`data-source-gleif`）。

いずれも**公開ライセンスの研究データ**を扱い、[`.itonami/profile.edn`](.itonami/profile.edn)
は記述（description）であって授権（grant）ではありません。この bot は資金・資格情報・
認証情報を保持せず、外部 contact も明示の承認なしには行いません。

## 境界と管轄

- データの収集と正規化は各 corpus bot（market-intel / gleif）が担う。
- この repo（charter）は管轄・境界・配信契約の正本であり、個々の収集そのものを
  実行する主体ではない（名簿と稼働の分離は manifest/repo-bots.edn と同じ規律）。
- 販売面は kotobase.net（x402）側の責務。本 repo は販売実行ではなく corpus の
  供給契約と境界を管理する。