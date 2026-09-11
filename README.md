# loop-data-source — itonami データソース事業の統括 charter repo

**名乗り:** `loop-data-source` は役割面（role plane, ADR-2608040100）の repo 名です。
この repo が所有するのは **itonami のデータソース事業** —— 公開ライセンスの研究データ
（SEC market-intel / GLEIF LEI）を収集・正規化して kotobase.net x402 で販売する
corpus を束ねる統括（charter/coordinator）です。実働の bot は Hermes profile
`data-source-market-intel` と `data-source-gleif` の 2 体で、この repo は両者の
管轄・境界・配信契約を宣言する場所です。

**operator として何をすればよいか**は [`docs/operator-quickstart.md`](docs/operator-quickstart.md)
が正本です —— 引用の取り直し方、exit の 3 値の読み方（**2 は合格ではない**）、
赤くなったときの判断表、買い手に約束してよいことの境界。

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
## 出所と条件 — [`catalog.edn`](catalog.edn)

上の 2 事業がどのエンドポイントから、どの条件でバイトを得るかは
[`catalog.edn`](catalog.edn) が正本です。charter が「配信契約を宣言する場所」で
ある以上、**何に対する契約なのか**がここに書かれていなければ境界ではありません。

```bash
# 全 13 引用を取り直し、ステータスと本文の両方を検査する
SEC_EDGAR_USER_AGENT="<your-app> <contact@example.com>" nbb bin/verify_sources.cljk
```

- 引用は**本文まで**検査します。200 を返しながら当の主張を載せなくなったページは、
  証拠として読まれる分だけ引用が無いより悪いためです。
- exit は 3 値で、**2 は「測れなかった」**（合格ではない）。SEC の User-Agent が
  未設定なら SEC 側 6 件は未検査のまま exit 2 になります。
- SEC の UA は commit しません（`SEC_EDGAR_USER_AGENT`。data-source-market-intel と
  同じ変数）。⚠ **URL 形の連絡先は 403 になります** —— メールアドレスを入れてください。

### 既知の境界: 2 つの corpus は `:company/lei` で join できない

SEC の `submissions` は `lei` フィールドを持ちますが、2026-09-09 に測った限り
**大手 20 社すべてで null**（全メガバンクを含む）。一方 GLEIF は同じ法人の LEI を
保持しています（JPMorgan Chase & Co. = `8I5DZWZKVSZI1NUHU748`）。つまり
**識別子が無いのではなく SEC 側が埋めていない**ので、join は GLEIF 側から
（名称等で）組み立てるほかなく、固有の誤り率を伴います。
**配信契約で key 一致の join を約束しないこと。** 詳細は `catalog.edn` の
`:catalog/boundary`。
