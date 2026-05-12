Exploration of the Marabou Resources Directory
================================================

> **Problem 1 — Survey of built-in benchmarks, models, and example queries**
> Source: https://github.com/NeuralNetworkVerification/Marabou/tree/master/resources

---

## Table of Contents

1. [Neural Network Models](#1-neural-network-models)
2. [Property / Specification Files](#2-property--specification-files)
3. [Example Scripts and Notebooks](#3-example-scripts-and-notebooks)
4. [Summary Table](#4-summary-table)
5. [Observations for Model Selection](#5-observations-for-model-selection)

---

## 1. Neural Network Models

### 1.1 `nnet/` — NNet format (`.nnet`)

Marabou's original native plain-text format encoding weights, biases, and input normalization.

| Sub-directory | Networks | Architecture | Task |
|---|---|---|---|
| `acasxu/` | 45 networks | 5-in · 6×50 hidden · 5-out | Aircraft collision avoidance advisories (Reluplex, Katz et al. 2017) |
| `coav/` | several | small FC | UAV collision avoidance (Planet paper) |
| `twin/` | several | small FC | Multi-output verification (TwinStreams) |
| `mnist/` | 1 (`mnist10x10.nnet`) | 10×10 hidden layers | Tiny MNIST classifier (parallelism demo) |

### 1.2 `onnx/` — ONNX format (`.onnx`)

Marabou 2.0 uses ONNX as its **primary format**. This directory contains small feed-forward networks for testing the ONNX parsing pipeline.

### 1.3 `keras/` — Keras / TensorFlow (`.pb` / SavedModel)

Networks exportable from TF/Keras, parsed via Marabou's TensorFlow interface.

### 1.4 `mps/` — Linear Programming (`.mps`)

LP benchmark files used for solver-level testing — not DNN verification.

### 1.5 `bnn_queries/` — Binary Neural Networks

Verification queries for BNNs using `{−1, +1}` weights, testing Marabou's BNN support.

---

## 2. Property / Specification Files

### ACAS Xu safety properties (`properties/acas_property_*.txt`)

| File | Property | Description |
|---|---|---|
| `acas_property_1.txt` | P1 | If intruder is far away, do **not** advise Strong Right turn |
| `acas_property_2.txt` | P2 | If intruder is far away, COC output must be maximal |
| `acas_property_3.txt` | P3 | COC is **not** the minimal advisory for a specific input region |
| `acas_property_4.txt` | P4 | COC must not be output in a specific dangerous scenario |

Each file specifies input bounds (box constraints) and output constraints in Marabou's line-by-line syntax. For example, `acas_property_1.txt` encodes: `x[0] ∈ [55947.691, 60760.0]`, `y[0] ≤ 3.9911256459`.

### MNIST properties (`properties/mnist/`)

Files like `image3_target6_epsilon0.05.txt` encode:
- L∞ bounds on all 784 pixel inputs around a reference image
- Output constraint: network must predict the true class

This is the same query structure implemented in `test.py`.

### `properties/builtin_property.txt`

A generic collision avoidance property embedded in the final network layer, used for `coav/` and `twin/` benchmarks.

---

## 3. Example Scripts and Notebooks

### `runMarabou.py`

Command-line runner demonstrating loading a `.nnet` model, loading a property file, and parallel verification with multiple workers:

```bash
./resources/runMarabou.py resources/nnet/mnist/mnist10x10.nnet \
  resources/properties/mnist/image3_target6_epsilon0.05.txt --num-workers=4
```

### `SplitAndConquerGuide.ipynb`

Jupyter notebook walkthrough of **Split-and-Conquer (SNC)** mode — decomposes a hard query into 2ⁿ sub-problems solved in parallel, dramatically reducing wall-clock time on large queries.

### `fashion.ipq`

A serialized Marabou internal query (`.ipq` format) for a Fashion-MNIST network. Can be loaded directly without going through ONNX/nnet parsing, useful for exact reproducibility of solver-level benchmarks.

---

## 4. Summary Table

| Category | Files / Formats | Notes |
|---|---|---|
| Network formats | `.nnet`, `.onnx`, `.pb` | ONNX is the primary format in v2.0 |
| Benchmark suites | ACAS Xu, coav, twin, MNIST, Fashion-MNIST | ACAS Xu is the canonical benchmark |
| Property format | `.txt` (custom syntax), `.vnnlib` | VNN-COMP standard format supported |
| Example scripts | `runMarabou.py`, `.ipynb` | Shows parallel + SNC usage |
| Serialized query | `.ipq` | Marabou internal format for reproducibility |

---

## 5. Observations for Model Selection

The following models are **already included** in the resources directory and must be excluded per the assignment requirements:

- All 45 ACAS Xu `.nnet` networks
- `mnist10x10.nnet` (tiny MNIST classifier)
- ONNX test networks in `onnx/`

**Selected approach for Problem 2:** Train a custom MNIST fully-connected network in PyTorch and export to `.onnx` (opset 11).

Rationale:
- ONNX is Marabou 2.0's primary supported format (`Marabou.read_onnx()`)
- A 784→64→32→10 architecture is small enough to avoid timeouts while being non-trivial
- MNIST provides unambiguous ground-truth labels and is the canonical local robustness benchmark
