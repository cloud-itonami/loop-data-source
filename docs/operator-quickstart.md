# operator quickstart — 供給契約が今日も成り立っているかを確かめる

この repo は **charter であって collector ではありません**。ここには収集する
コードは 1 行も無く、在るのは「どのバイトを、どの条件で売ってよいか」の宣言
（[`catalog.edn`](../catalog.edn)）と、その宣言が**今日もまだ真であること**を
測る道具（[`bin/verify_sources.cljk`](../bin/verify_sources.cljk)）だけです。

したがって operator の仕事はちょうど 1 つです:

> **配信契約の土台になっている 13 の引用を取り直し、まだ同じことを言っているか
> 確かめる。言っていなければ、何を約束し直すかを決める。**

実際に収集を回している bot はここには居ません（§6）。

---

## 1. 前提

```bash
nbb --version     # 実測 2026-09-09: v1.5.212
node --version    # 実測 2026-09-09: v26.7.0
```

**それだけです。** この repo に `deps.edn` は無く、verifier は nbb 同梱の
`clojure.edn` / `clojure.string` と `node:fs` しか使いません。superproject も
west も要らないので、**素の `git clone` した tree の中でそのまま走ります**
（この文書の全実測は west checkout から切った worktree、`/tmp` 配下で採りました）。

west 経由で見ているなら path は `orgs/cloud-itonami/loop-data-source` です。

## 2. SEC の User-Agent を用意する（設定はこれだけ）

13 引用のうち **6 つが SEC** で、SEC は名乗らない呼び出し元を拒否します
（`:sec/access-policy` = webmaster FAQ の "Please declare your user agent in
request headers"）。GLEIF 側は認証も連絡先も要りません。

```bash
export SEC_EDGAR_USER_AGENT="<your-app>/<version> <あなたが実際に読むメールアドレス>"
```

⚠ **連絡先は「メールアドレスの形」でなければなりません。URL を入れると 403 です。**
FAQ には書かれておらず、**間違え方がネットワーク障害の顔をして返ってきます**。
実測 2026-09-09、同じ URL・同じ client で両方向を確認:

```console
$ U="https://www.sec.gov/files/company_tickers.json"
$ curl -s -o /dev/null -w "%{http_code}\n" -A "itonami-data-source/1.0 data-source@itonami.cloud" "$U"
200
$ curl -s -o /dev/null -w "%{http_code}\n" -A "itonami-data-source/1.0 (+https://github.com/cloud-itonami/loop-data-source)" "$U"
403
```

**この変数は commit しません。** 変数名は collector 側
（`network-awai/cloud-murakumo-market-intel` の README）と同じものを使っており、
charter が 2 つ目の作法を発明しないためです。

## 3. 走らせる

```bash
nbb bin/verify_sources.cljk            # 13 引用。実測 2026-09-09 で 9 秒
nbb bin/verify_sources.cljk --quiet    # 集計行だけ
```

要求は **1 本ずつ直列**に出ます。SEC の上限が 10 req/s なので、直列である限り
rate limiter が要りません。**並列化しないでください。**

green の形:

```
CHECKED	13	ok=13	fail=0	unreachable=0
OK: every citation resolved and still says what the catalog says it says.
```

`CHECKED` の行は evidence floor です —— **「何も検査しなかった」が
「何も問題が無かった」と読めないように**、必ず実検査数を印字します。

## 4. exit を読む（3 値。**2 は合格ではありません**）

| exit | 意味 | あなたがすること |
|---|---|---|
| **0** | 13 件すべてに到達し、すべて一致した | 何もしなくてよい |
| **1** | 到達したが**一致しなかった** | §5 の判断表へ。実在の欠陥 |
| **2** | **到達できなかった / 検査対象が無かった** | **合格として扱わない。** 何も学べていない |

exit 2 が独立している理由は、「測れなかった」と「測って問題が無かった」が
同じ値で返ると、沈黙が緑として蓄積するからです。SEC の UA を設定せずに走らせた
ときが典型で、実測ではこうなります（**7 件は本当に緑、6 件は未検査**）:

```
CHECKED	13	ok=7	fail=0	unreachable=6
UNVERIFIED: 6 citation(s) could not be reached. This is not a pass — nothing was learned about them.
```

`fail` は `unreachable` より優先されます（1 件でも不一致が在れば exit 1）。

## 5. 赤くなったときの判断表

**まず「何件が、どの群で」落ちたかを見てください。** 原因の切り分けはそこで付きます。

### (a) SEC の 6 件が**まとめて** `got 403` で落ちた → あなたの UA を疑う

```
FAIL  company-tickers — expected HTTP 200, got 403
FAIL  submissions — expected HTTP 200, got 403
...  (6 件すべて)
CHECKED	13	ok=7	fail=6	unreachable=0
```

これは **catalog の欠陥ではありません。** ⚠ この形が厄介なのは 2 つの理由です:

1. exit **1**（＝「実在の欠陥」）で出るので、上流が壊れた顔をする。
2. **ヘッダは `sec-ua set` と言い続けます** —— 設定されているかしか見ておらず、
   *形*は見ていないため。

**先に §2 の curl を 1 本打ってください。** ここで catalog の quote を直しに
行くと、正しい引用を壊すことになります。

### (b) `[TRIPWIRE ...]` が付いた 1 件が落ちた → **quote を短くしない**

```
FAIL  submissions — HTTP 200 as expected, but the payload no longer contains: "\"lei\":null"
      [TRIPWIRE — this was expected to change one day; go re-read :catalog/boundary]
```

tripwire は**壊れたのではなく、鳴ったのです。** `"lei":null` は「SEC が LEI 欄を
埋めていない」という現在地を固定していて、この repo の join 境界（§6）はその上に
載っています。これが赤くなったということは、**SEC が埋め始めた可能性がある**
ということで、そのとき変わるのは catalog ではなく**買い手への約束**です。

順序: `:catalog/boundary` を読み直す → 実際に何社で埋まったか測り直す →
境界の記述を更新する → **最後に** quote を更新する。
**quote を通るまで削るのは、通知線を切る操作です。**

### (c) 単発の 1 件が `payload no longer contains` で落ちた → 上流が変わった

その引用が支えていた主張ごと直します。catalog の該当箇所を直すだけでは足りず、
**その引用に寄りかかっていた記述**（licence の根拠、endpoint が supported である
根拠など）が今も成り立つかを確かめてください。

### (d) exit 2 で `could not reach` → ネットワークか上流の停止

再実行してよい唯一のケースです。**ただし直るまで「検査済み」と書かない。**

## 6. 買い手に約束してよいこと・いけないこと

⚠ **2 つの corpus を `:company/lei` の key 一致で join できると約束しないでください。**

workspace の query 面は `:company/lei` を結合キーに使いますが、実測 2026-09-09、
**SEC 側からはその join ができません** —— `:sec/submissions` は `lei` 欄を持ち
（スキーマを読んだ collector は素直に配線してしまう）、大手 20 社すべてで
**null（0/20、全メガバンクを含む）** でした。識別子が無いのではなく SEC が
埋めていないだけで、GLEIF は同じ法人の LEI を持っています。

これが危険なのは、**null 欄と欠落欄が下流で同じ顔をする**からです。join した
corpus は 0 行を返し、個々の fetch はすべて成功を報告します。

正本は `catalog.edn` の `:catalog/boundary`、その反証プローブは
`:gleif/lei-record-jpmorgan`（verifier が毎回検査しています）。

## 7. 直したあとに更新するもの

- `catalog.edn` の **`:catalog/verified-on`** —— 最後に 13 件が緑になった日。
- 境界を測り直したなら `:boundary/measured-on` と `:boundary/sampled` /
  `:boundary/sec-lei-populated`。
- **緑にできなかったなら、日付を進めない。** 進めた日付は「その日に測った」と
  読まれます。

## 付録 — この文書の主張をどう再現するか

数値ではなく手順を残します（値は今日のもので、手順は来週も効きます）。

| 主張 | 再現 |
|---|---|
| exit 0 / 1 / 2 が実際に分かれる | §3・§4 のコマンド |
| verifier は本当に不一致を捕まえる | catalog の写しで quote を 1 つ壊し、**その 1 件だけ**が FAIL になり exit 1 になることを見る |
| tripwire は註釈付きで鳴る | 同じく `:sec/submissions` の `"lei":null` を写しの側で別文字列に変える |
| UA の形が 403 を決めている | §2 の curl 2 本 |

⚠ **壊して赤くする実演は、必ず `diff` で「壊したのはそこだけ」を確かめてから
読んでください。** 置換が当たらずに緑のままだったものを「実演できた」と
読むのが、この種の検査で最も安い失敗です（この文書を書いた反復で 1 回踏みました）。
