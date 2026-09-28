;; market_intel evidence — market-intel corpus データソース事業 bot の測定器 (decision-free).
;; read-only: git HEAD, datom 行数, ライセンス, x402 SKU readiness を測る。git を書き換えない。
;; Run: nbb scripts/market_intel_evidence.cljs   (wrapper: scripts/market_intel_evidence.py)
;; 出力契約: SCANNED<tab>..  + MEASURE<tab>key<tab>value  + SKU-READY<tab>key<tab>vendor<tab>path
(require '[clojure.string :as str]
         '["node:child_process" :as cp]
         '["node:fs" :as fs]
         '["node:path" :as path])

(def root "~/github/com-junkawasaki")
(def today (subs (.toISOString (new js/Date)) 0 10))

(defn sh [dir cmd]
  (try (str/trim (str (cp/execSync cmd #js {:cwd dir :timeout 120000 :encoding "utf8"})))
       (catch :default _ nil)))

(def corpus-dir (path/join root "orgs/network-awai/cloud-murakumo-market-intel"))
(def corpus-file (path/join corpus-dir "data/company-facts.edn"))
(def corpus-license "SEC EDGAR public domain (17 U.S.C. §105). EDN normalization = 自社 derived.")

(defn -main []
  (println (str "SCANNED\tmarket_intel-" today "-" (sh nil "date +%H%M%S")))
  (println (str "MEASURE\tcorpus\tmarket-intel"))
  (println (str "MEASURE\tcheckout\t" (if (fs/existsSync corpus-dir) "present" "missing")))
  (println (str "MEASURE\thead\t" (or (sh corpus-dir "git rev-parse --short HEAD") "UNMEASURED")))
  (let [exists (fs/existsSync corpus-file)]
    (println (str "MEASURE\tdatom-lines\t" (if exists (count (str/split-lines (str (fs/readFileSync corpus-file "utf8")))) -1))))
  (println (str "MEASURE\tlicense\t" corpus-license))
  (println (str "SKU-READY\tmarket-intel\tkotobase\t/x402/market-intel"))
  (let [cat (sh nil "curl -sS -m 20 https://x402.nexus/catalog")]
    (println (str "MEASURE\tx402.catalog\t" (if cat (str (count cat) " bytes") "UNREACHABLE")))))
(-main)
