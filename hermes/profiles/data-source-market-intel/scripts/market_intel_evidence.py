#!/usr/bin/env python3
"""Measurements for the market-intel data-source corpus bot.

Decision-free. Runs the .cljs collector (nbb) via this wrapper because Hermes
cron executes --script files as bash/python. REFUSED banner on failure so the
bot is told it is blind, never that the data is ready. Throttled to 24h.
"""
import os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from throttle import gate, mark  # noqa: E402

NBB = os.environ.get("HYAKKA_NBB", "/opt/homebrew/bin/nbb")
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
JOB = "market-intel"
COOLDOWN_H = float(os.environ.get("DATA_SOURCE_COOLDOWN_HOURS", "24"))

def refuse(why):
    print("REFUSED — no evidence was gathered this run.")
    print(why)
    print("Do not propose anything. Report this refusal and stop.")
    sys.exit(0)

def main():
    gate(JOB, hours=COOLDOWN_H)
    proc = subprocess.run([NBB, os.path.join(SCRIPT_DIR, "market_intel_evidence.cljs")],
                          capture_output=True, text=True, timeout=600)
    if proc.returncode == 2:
        refuse("collector refused:\n" + proc.stderr.strip()[:800])
    if proc.returncode != 0:
        refuse(f"collector exited {proc.returncode}:\n" + (proc.stderr.strip() or proc.stdout.strip())[:800])
    if "SCANNED" not in proc.stdout:
        refuse("no SCANNED line")
    mark(JOB)
    print(proc.stdout.strip())

if __name__ == "__main__":
    main()
