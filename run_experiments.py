"""
run_experiments.py

Two-phase experiment:

  Phase 1 — Sample Scan
    Sweep sample indices 0..99 at a fixed epsilon (0.05) with a short timeout (60s).
    Goal: find samples that produce SAT (adversarial example found).

  Phase 2 — Epsilon Sweep on Interesting Samples
    For the first SAT sample found and for the original index-0 (all-UNSAT baseline),
    run a detailed epsilon sweep from 0.01 to 0.20.
    Goal: compare robustness boundary between a robust and a non-robust sample.

Results are written to results/results.md.
"""

import subprocess
import time
import os

MARABOU_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Marabou_src")
SCAN_EPSILON  = 0.05
SCAN_TIMEOUT  = 60          # seconds per query in Phase 1
SWEEP_TIMEOUT = 300         # seconds per query in Phase 2
SWEEP_EPSILONS = [round(x * 0.01, 2) for x in range(1, 21)]
MAX_SCAN_IDX  = 100

env = os.environ.copy()
env["PYTHONPATH"] = MARABOU_PATH
os.makedirs("results", exist_ok=True)


def run_test(sample_idx, epsilon, timeout):
    cmd = [
        "python", "test.py",
        "--epsilon",    str(epsilon),
        "--sample-idx", str(sample_idx),
        "--timeout",    str(timeout),
    ]
    t0 = time.time()
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True, env=env)
    stdout, _ = proc.communicate()
    elapsed = time.time() - t0

    if "Verdict:  UNSAT" in stdout:
        verdict = "UNSAT"
    elif "Verdict:  SAT" in stdout:
        verdict = "SAT"
    elif elapsed >= timeout - 1:
        verdict = "TIMEOUT"
    else:
        verdict = "UNKNOWN"

    adv_class = None
    for line in stdout.splitlines():
        if "Adversarial class predicted:" in line:
            # Line: "  Adversarial class predicted: X  (true: Y)" — take first token after ":"
            after_colon = line.split("Adversarial class predicted:")[-1].strip()
            adv_class = after_colon.split()[0]

    return verdict, round(elapsed, 2), adv_class


# ── Phase 1: Sample Scan ──────────────────────────────────────────────────────
print("=" * 60)
print(f"Phase 1: Sample Scan  (ε={SCAN_EPSILON}, timeout={SCAN_TIMEOUT}s)")
print("=" * 60)

sat_samples   = []   # (idx, label_inferred, elapsed)
unsat_samples = []

with open("results/results.md", "w") as f:
    f.write("# Verification Experiment Results\n\n")
    f.write("## Phase 1 — Sample Scan\n\n")
    f.write(f"Fixed ε = {SCAN_EPSILON}, timeout = {SCAN_TIMEOUT}s, samples 0–{MAX_SCAN_IDX-1}\n\n")
    f.write(f"| Sample idx | Verdict | Runtime |\n")
    f.write(f"|:---:|:---:|---:|\n")

for idx in range(MAX_SCAN_IDX):
    verdict, elapsed, adv_class = run_test(idx, SCAN_EPSILON, SCAN_TIMEOUT)
    flag = " ← SAT" if verdict == "SAT" else ""
    print(f"  idx={idx:3d} | {verdict:7s} | {elapsed:6.2f}s{flag}")

    with open("results/results.md", "a") as f:
        f.write(f"| {idx} | **{verdict}** | {elapsed:.2f}s |\n")

    if verdict == "SAT":
        sat_samples.append((idx, adv_class, elapsed))
        if len(sat_samples) >= 3:   # collect up to 3 SAT samples then stop
            print(f"\n  Found {len(sat_samples)} SAT samples — stopping scan early.")
            break
    elif verdict == "UNSAT":
        unsat_samples.append(idx)

print(f"\nPhase 1 done.  SAT samples: {[s[0] for s in sat_samples]}")

with open("results/results.md", "a") as f:
    f.write(f"\n**SAT samples found:** {[s[0] for s in sat_samples]}\n\n")


# ── Phase 2: Epsilon Sweep ────────────────────────────────────────────────────
sweep_targets = []

# Always include the original baseline (index 0)
if 0 not in [s[0] for s in sat_samples]:
    sweep_targets.append((0, "baseline (all-UNSAT)"))

# Add up to 2 SAT samples
for idx, adv_class, _ in sat_samples[:2]:
    sweep_targets.append((idx, f"SAT sample (adv→{adv_class})"))

print("\n" + "=" * 60)
print(f"Phase 2: Epsilon Sweep  (ε=0.01→0.20, timeout={SWEEP_TIMEOUT}s)")
print("=" * 60)

with open("results/results.md", "a") as f:
    f.write("## Phase 2 — Epsilon Sweep\n\n")

for sample_idx, label in sweep_targets:
    print(f"\n  Sample idx={sample_idx}  [{label}]")
    print(f"  {'ε':>6}  {'Verdict':>7}  {'Runtime':>8}")
    print(f"  {'------':>6}  {'-------':>7}  {'-------':>8}")

    with open("results/results.md", "a") as f:
        f.write(f"### Sample {sample_idx} — {label}\n\n")
        f.write("| ε | Verdict | Runtime |\n")
        f.write("|:---:|:---:|---:|\n")

    for eps in SWEEP_EPSILONS:
        verdict, elapsed, adv_class = run_test(sample_idx, eps, SWEEP_TIMEOUT)
        adv_str = f"  adv→{adv_class}" if adv_class else ""
        print(f"  {eps:6.2f}  {verdict:>7}  {elapsed:7.2f}s{adv_str}")

        with open("results/results.md", "a") as f:
            adv_col = f" (adv→{adv_class})" if adv_class else ""
            f.write(f"| {eps:.2f} | **{verdict}**{adv_col} | {elapsed:.2f}s |\n")

        if verdict == "TIMEOUT" and eps >= 0.15:
            print(f"  [skipping remaining epsilons for this sample]")
            with open("results/results.md", "a") as f:
                f.write("| >0.15 | TIMEOUT | — |\n")
            break

    with open("results/results.md", "a") as f:
        f.write("\n")

print("\nAll experiments completed. Results written to results/results.md")
