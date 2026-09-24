# hermes/ — the resident bots that act for this repository

This directory is the **source of truth** for the Hermes profiles listed below
(ADR-2609241200). The host's `~/.hermes/profiles/<profile>` is materialized
from `hermes/profiles/<profile>/` and checked against it:

```
kbb --backend sci scripts/hermes-profile-repo.cljk materialize <profile>   # repo -> host
kbb --backend sci scripts/hermes-profile-repo.cljk check <profile>         # 0 agree / 1 drift / 2 could not compare
kbb --backend sci scripts/hermes-profile-repo.cljk export <profile>        # host -> repo, then commit
```

(run from the com-junkawasaki/root superproject; registry
`manifest/hermes-profile-repos.edn`.)

Each profile directory holds SOUL.md, profile.yaml, config.yaml (host-local
blocks removed), cron/jobs.json (definitions only), scripts/ and the skills the
profile owns. **Never here:** `.env` or any secret value, workspace/ledgers,
sessions, memories, logs, caches, run state.

## Profiles

| profile | description |
|---|---|
| `data-source` | data-source — itonami データソース事業 bot: 公開ライセンス corpus (market-intel SEC / GLEIF LEI 等) を収集・正規化し datom plane / lake へ同期し、kotobase.net の x402 販売 SKU 候補を提案する（1 tick = |
| `data-source-gleif` | data-source / gleif-lei — itonami データソース事業 corpus bot. 対象 corpus: gleif-lei (com-junkawasaki/org-gleif-projections). 毎 tick、鮮度(HEAD)+datom 行数+ライセンス+x402 SKU rea |
| `data-source-market-intel` | data-source / market-intel — itonami データソース事業 corpus bot. 対象 corpus: market-intel (network-awai/cloud-murakumo-market-intel). 毎 tick、鮮度(HEAD)+datom 行数+ライセンス+x40 |
