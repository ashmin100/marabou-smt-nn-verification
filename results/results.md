# Verification Experiment Results

## Phase 1 — Sample Scan

Fixed ε = 0.05, timeout = 60s, samples 0–99

| Sample idx | Verdict | Runtime |
|:---:|:---:|---:|
| 0 | **UNSAT** | 0.71s |
| 1 | **UNSAT** | 0.47s |
| 2 | **UNSAT** | 0.48s |
| 3 | **UNSAT** | 0.44s |
| 4 | **UNSAT** | 0.46s |
| 5 | **UNSAT** | 0.46s |
| 6 | **UNSAT** | 0.48s |
| 7 | **UNSAT** | 0.47s |
| 8 | **SAT** | 0.87s |
| 9 | **UNSAT** | 0.48s |
| 10 | **UNSAT** | 0.49s |
| 11 | **UNSAT** | 0.51s |
| 12 | **UNSAT** | 0.49s |
| 13 | **UNSAT** | 0.47s |
| 14 | **UNSAT** | 0.51s |
| 15 | **UNSAT** | 0.48s |
| 16 | **UNSAT** | 0.52s |
| 17 | **UNSAT** | 0.47s |
| 18 | **UNSAT** | 0.58s |
| 19 | **UNSAT** | 0.48s |
| 20 | **UNSAT** | 0.46s |
| 21 | **UNSAT** | 0.50s |
| 22 | **UNSAT** | 0.50s |
| 23 | **UNSAT** | 0.49s |
| 24 | **UNSAT** | 0.49s |
| 25 | **UNSAT** | 0.52s |
| 26 | **UNSAT** | 0.43s |
| 27 | **UNSAT** | 0.46s |
| 28 | **UNSAT** | 0.48s |
| 29 | **UNSAT** | 0.51s |
| 30 | **UNSAT** | 0.51s |
| 31 | **UNSAT** | 0.63s |
| 32 | **UNSAT** | 0.49s |
| 33 | **SAT** | 0.49s |
| 34 | **UNSAT** | 0.52s |
| 35 | **UNSAT** | 0.54s |
| 36 | **UNSAT** | 0.54s |
| 37 | **UNSAT** | 0.51s |
| 38 | **UNSAT** | 0.56s |
| 39 | **UNSAT** | 0.54s |
| 40 | **UNSAT** | 0.47s |
| 41 | **UNSAT** | 0.50s |
| 42 | **UNSAT** | 0.50s |
| 43 | **UNSAT** | 0.49s |
| 44 | **UNSAT** | 0.50s |
| 45 | **UNSAT** | 0.47s |
| 46 | **UNSAT** | 0.49s |
| 47 | **UNSAT** | 0.54s |
| 48 | **UNSAT** | 0.48s |
| 49 | **UNSAT** | 0.50s |
| 50 | **UNSAT** | 0.50s |
| 51 | **UNSAT** | 0.48s |
| 52 | **UNSAT** | 0.45s |
| 53 | **UNSAT** | 0.51s |
| 54 | **UNSAT** | 0.47s |
| 55 | **UNSAT** | 0.49s |
| 56 | **UNSAT** | 0.47s |
| 57 | **UNSAT** | 0.45s |
| 58 | **UNSAT** | 0.49s |
| 59 | **UNSAT** | 0.48s |
| 60 | **UNSAT** | 0.48s |
| 61 | **UNSAT** | 0.41s |
| 62 | **UNSAT** | 4.57s |
| 63 | **UNSAT** | 2.19s |
| 64 | **UNSAT** | 0.47s |
| 65 | **UNSAT** | 1.36s |
| 66 | **UNSAT** | 33.70s |
| 67 | **UNSAT** | 0.51s |
| 68 | **UNSAT** | 0.45s |
| 69 | **UNSAT** | 0.49s |
| 70 | **UNSAT** | 0.51s |
| 71 | **UNSAT** | 0.50s |
| 72 | **UNSAT** | 0.49s |
| 73 | **UNSAT** | 0.49s |
| 74 | **UNSAT** | 0.47s |
| 75 | **UNSAT** | 0.45s |
| 76 | **UNSAT** | 0.50s |
| 77 | **UNSAT** | 0.51s |
| 78 | **UNSAT** | 0.50s |
| 79 | **UNSAT** | 0.47s |
| 80 | **UNSAT** | 0.60s |
| 81 | **UNSAT** | 0.50s |
| 82 | **UNSAT** | 0.52s |
| 83 | **UNSAT** | 0.48s |
| 84 | **UNSAT** | 0.49s |
| 85 | **UNSAT** | 0.45s |
| 86 | **UNSAT** | 0.44s |
| 87 | **UNSAT** | 0.53s |
| 88 | **UNSAT** | 0.54s |
| 89 | **UNSAT** | 0.48s |
| 90 | **UNSAT** | 0.49s |
| 91 | **UNSAT** | 0.48s |
| 92 | **SAT** | 0.55s |

**SAT samples found:** [8, 33, 92]

## Phase 2 — Epsilon Sweep

### Sample 0 — baseline (all-UNSAT)

| ε | Verdict | Runtime |
|:---:|:---:|---:|
| 0.01 | **UNSAT** | 0.39s |
| 0.02 | **UNSAT** | 0.42s |
| 0.03 | **UNSAT** | 0.51s |
| 0.04 | **UNSAT** | 0.53s |
| 0.05 | **UNSAT** | 0.48s |
| 0.06 | **UNSAT** | 0.48s |
| 0.07 | **UNSAT** | 0.48s |
| 0.08 | **UNSAT** | 0.49s |
| 0.09 | **UNSAT** | 0.52s |
| 0.10 | **UNSAT** | 0.91s |
| 0.11 | **UNSAT** | 1.02s |
| 0.12 | **UNSAT** | 6.17s |
| 0.13 | **UNSAT** | 3.57s |
| 0.14 | **UNSAT** | 8.90s |
| 0.15 | **UNSAT** | 14.28s |
| 0.16 | **UNSAT** | 25.79s |
| 0.17 | **UNSAT** | 38.15s |
| 0.18 | **UNSAT** | 138.94s |
| 0.19 | **UNSAT** | 300.54s |
| 0.20 | **UNSAT** | 300.48s |

### Sample 8 — SAT sample (adv→5))

| ε | Verdict | Runtime |
|:---:|:---:|---:|
| 0.01 | **UNSAT** | 0.52s |
| 0.02 | **UNSAT** | 0.58s |
| 0.03 | **SAT** (adv→5)) | 0.51s |
| 0.04 | **SAT** (adv→5)) | 0.56s |
| 0.05 | **SAT** (adv→5)) | 0.83s |
| 0.06 | **SAT** (adv→5)) | 0.59s |
| 0.07 | **SAT** (adv→5)) | 0.61s |
| 0.08 | **SAT** (adv→5)) | 1.05s |
| 0.09 | **SAT** (adv→5)) | 0.88s |
| 0.10 | **SAT** (adv→5)) | 0.92s |
| 0.11 | **SAT** (adv→5)) | 1.58s |
| 0.12 | **SAT** (adv→5)) | 9.25s |
| 0.13 | **SAT** (adv→5)) | 16.55s |
| 0.14 | **SAT** (adv→5)) | 82.15s |
| 0.15 | **SAT** (adv→5)) | 1.08s |
| 0.16 | **SAT** (adv→5)) | 0.78s |
| 0.17 | **SAT** (adv→5)) | 0.61s |
| 0.18 | **SAT** (adv→5)) | 0.74s |
| 0.19 | **SAT** (adv→5)) | 0.62s |
| 0.20 | **SAT** (adv→5)) | 0.62s |

### Sample 33 — SAT sample (adv→4))

| ε | Verdict | Runtime |
|:---:|:---:|---:|
| 0.01 | **UNSAT** | 0.48s |
| 0.02 | **UNSAT** | 0.49s |
| 0.03 | **UNSAT** | 0.54s |
| 0.04 | **UNSAT** | 0.56s |
| 0.05 | **SAT** (adv→4)) | 0.53s |
| 0.06 | **SAT** (adv→4)) | 0.55s |
| 0.07 | **SAT** (adv→4)) | 0.51s |
| 0.08 | **SAT** (adv→4)) | 0.52s |
| 0.09 | **SAT** (adv→4)) | 0.52s |
| 0.10 | **SAT** (adv→4)) | 0.58s |
| 0.11 | **SAT** (adv→4)) | 0.49s |
| 0.12 | **SAT** (adv→4)) | 0.53s |
| 0.13 | **SAT** (adv→4)) | 0.54s |
| 0.14 | **SAT** (adv→4)) | 0.57s |
| 0.15 | **SAT** (adv→4)) | 0.49s |
| 0.16 | **SAT** (adv→4)) | 0.52s |
| 0.17 | **SAT** (adv→4)) | 0.51s |
| 0.18 | **SAT** (adv→4)) | 0.55s |
| 0.19 | **SAT** (adv→4)) | 0.57s |
| 0.20 | **SAT** (adv→4)) | 0.54s |

