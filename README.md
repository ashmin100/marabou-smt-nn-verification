# Neural Network Verification with Marabou

> Formal, SMT-based local robustness verification of an MNIST classifier — proving that no adversarial perturbation within an L∞ ball can flip the predicted class.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![Framework](https://img.shields.io/badge/Verifier-Marabou%202.0-orange)
![Model](https://img.shields.io/badge/Model-ONNX%20opset%2011-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Overview

This project applies [Marabou](https://github.com/NeuralNetworkVerification/Marabou) (Katz et al., CAV 2019) to formally verify **local robustness** of a small fully-connected network trained on MNIST.

Unlike gradient-based attacks (FGSM, PGD) that only *search* for adversarial examples, Marabou gives a **complete proof**: an UNSAT result guarantees that *no* input within the perturbation region can change the predicted class.

```
∀x' s.t. ‖x' − x‖_∞ ≤ ε  ⟹  argmax f(x') = d
```

---

## Key Results

Two-phase experiment: (1) scan 100 test images at ε=0.05 to find SAT samples, (2) sweep ε ∈ [0.01, 0.20] on three representative samples.

**Robustness boundaries per sample:**

| Sample | True Label | ε* (boundary) | Certified up to | Adversarial class |
|:------:|:----------:|:-------------:|:---------------:|:-----------------:|
| idx=0 | 7 | > 0.20 | ≥ 0.20 (full range) | — |
| idx=8 | 5 | ≈ 0.03 | 0.02 | 6 |
| idx=33 | 4 | ≈ 0.05 | 0.04 | 0 |

**Runtime comparison at selected ε:**

| ε (normalized) | ε (÷255) | idx=0 runtime | idx=8 runtime | idx=33 runtime |
|:--------------:|:--------:|:-------------:|:-------------:|:--------------:|
| 0.03 | ~2.4/255 | UNSAT  0.5s | **SAT  0.5s** | UNSAT  0.5s |
| 0.05 | ~4.0/255 | UNSAT  0.5s | SAT  0.8s | **SAT  0.5s** |
| 0.15 | ~12.1/255 | UNSAT  14.3s | SAT  1.1s | SAT  0.5s |
| 0.20 | ~16.2/255 | UNSAT  300.5s | SAT  0.6s | SAT  0.5s |

> **Key insight:** SAT queries terminate in sub-second (witness found immediately). UNSAT at large ε requires exhausting a 2^96 branch-and-bound tree — up to 300 s. This asymmetry is intrinsic to complete verification of an NP-hard property.
>
> **False SAT fix:** Removing physical bounds clamping (`[-0.4242, 2.8215]`) inflated ε=0.12 runtime from 6s → 248s and produced a spurious SAT at ε=0.15.

---

## Architecture

```
MNIST image (28×28)
       │
       ▼
  Flatten → [784]
       │
  Linear(784→64) + ReLU
       │
  Linear(64→32)  + ReLU
       │
  Linear(32→10)
       │
  argmax → predicted digit
```

**Test accuracy:** ~97.5%  |  **Format:** ONNX opset 11  |  **Parameters:** ~55,000

---

## Setup

### 1. Build Marabou from source

```bash
# macOS dependencies
brew install cmake boost wget

# Clone and build
git clone https://github.com/NeuralNetworkVerification/Marabou/
cd Marabou && mkdir build && cd build
cmake ../ -DCMAKE_POLICY_VERSION_MINIMUM=3.5
cmake --build . -j 4
```

### 2. Set PYTHONPATH

```bash
export PYTHONPATH=/path/to/Marabou:$PYTHONPATH
```

Replace `/path/to/Marabou` with the actual cloned directory path.

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

---

## Usage

**Step 1 — Train & export model**

```bash
python train_model.py
```

Outputs: `models/mnist_fc.onnx`, `models/sample_inputs.npy`, `models/sample_labels.npy`

**Step 2 — Run a single verification query**

```bash
python test.py [--epsilon FLOAT] [--sample-idx INT] [--timeout INT]
```

| Flag | Default | Description |
|------|:-------:|-------------|
| `--epsilon` | `0.01` | L∞ perturbation radius (normalized) |
| `--sample-idx` | `0` | Index into saved test samples |
| `--timeout` | `300` | Solver timeout in seconds |

```bash
python test.py --epsilon 0.05 --sample-idx 8    # SAT — adversarial example found
python test.py --epsilon 0.15 --sample-idx 0    # UNSAT — certified robust
```

**Step 3 — Run two-phase experiment sweep**

```bash
python run_experiments.py
# Phase 1: scan samples 0–99 at ε=0.05 to find SAT samples
# Phase 2: sweep ε=0.01→0.20 on baseline + discovered SAT samples
# Output: results/results.md
```

**Step 4 — Visualize results**

```bash
python visualize_results.py
# Generates 3-sample runtime bar charts + verdict heatmap
# Output: results/verification_results.png
```

---

## Expected Output (SAT example)

```
============================================================
Marabou Local Robustness Verification
============================================================
  Sample idx:  8  (true label: 5)
  Epsilon:     0.03  (L-inf ball)
============================================================
  Verdict:  SAT (counterexample found)
  Meaning:  An adversarial input exists within the L-inf ball.

  Adversarial class predicted: 6  (true: 5)
  Max perturbation (L-inf):    0.029997
  Output logits (adversarial): [-2.1  0.8  1.3  0.4  2.1  4.9  5.1 -0.9  1.2  0.6]
============================================================
```

---

## Repository Structure

```
.
├── README.md
├── requirements.txt
├── train_model.py          # Train MNIST FC network + ONNX export
├── test.py                 # Marabou verification query (main entry point)
├── run_experiments.py      # Two-phase experiment (sample scan + ε sweep)
├── visualize_results.py    # Runtime bar charts + verdict heatmap
├── exploration_report.md   # Survey of Marabou built-in resources (Problem 1)
├── report.md               # Analysis report (EN)
├── report_ko.md            # Analysis report (KO)
├── models/
│   ├── mnist_fc.onnx       # Trained model (generated by train_model.py)
│   ├── sample_inputs.npy   # Test samples  (generated)
│   └── sample_labels.npy   # Labels        (generated)
└── results/
    ├── results.md                  # Full sweep results table
    └── verification_results.png   # Runtime + verdict visualization
```

---

## References

- Katz, G. et al. *The Marabou Framework for Verification and Analysis of Deep Neural Networks.* CAV 2019.
- Szegedy, C. et al. *Intriguing Properties of Neural Networks.* ICLR 2014.
