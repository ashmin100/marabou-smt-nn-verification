# Marabou MNIST Robustness Verification

Formal verification of neural network local robustness using [Marabou](https://github.com/NeuralNetworkVerification/Marabou).

A small fully-connected network trained on MNIST is verified against L-inf perturbation attacks using SMT-based complete verification.

## What this does

- Trains a 784→64→32→10 FC network on MNIST (>97% test accuracy)
- Exports it to ONNX format
- Uses Marabou to formally verify: *"For a given input x classified as digit d, all inputs x' with ||x'−x||∞ ≤ ε are also classified as d"*

## Setup

### 1. Build Marabou from source

Marabou must be built from source (Python 3.8–3.11 pip wheels are available,
but source build is used here to support any Python version).

```bash
# Install build dependencies (macOS)
brew install cmake boost wget

# Clone and build
git clone https://github.com/NeuralNetworkVerification/Marabou/
cd Marabou
mkdir build && cd build
cmake ../ -DCMAKE_POLICY_VERSION_MINIMUM=3.5
cmake --build . -j 4
```

### 2. Set PYTHONPATH

```bash
export PYTHONPATH=/path/to/Marabou:$PYTHONPATH
```

Replace `/path/to/Marabou` with the actual path to your cloned Marabou directory.

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

## Running

### Step 1 — Train the model

```bash
python train_model.py
```

Trains the MNIST FC network for 5 epochs and saves:
- `models/mnist_fc.onnx` — the exported model
- `models/sample_inputs.npy` — correctly-classified test samples
- `models/sample_labels.npy` — corresponding labels

### Step 2 — Run Marabou verification

```bash
python test.py
```

Optional arguments:

| Flag | Default | Description |
|------|---------|-------------|
| `--epsilon` | `0.01` | L-inf perturbation radius |
| `--sample-idx` | `0` | Which sample to verify |
| `--timeout` | `300` | Verification timeout (seconds) |

Example with custom epsilon:

```bash
python test.py --epsilon 0.005 --sample-idx 3
```

## Expected output

```
============================================================
Marabou Local Robustness Verification
============================================================
  Model:       models/mnist_fc.onnx
  Sample idx:  0  (true label: 7)
  Epsilon:     0.01  (L-inf ball)
  Timeout:     300s
============================================================
...
RESULT
============================================================
  Verification time: 12.43s
  Verdict:  UNSAT
  Meaning:  The network always predicts class 7
            for all inputs within the L-inf ball of radius 0.01.
```

## Repository structure

```
.
├── README.md
├── requirements.txt
├── train_model.py      # Train MNIST FC + export to ONNX
├── test.py             # Marabou verification query
├── exploration.md      # Survey of Marabou built-in resources
├── report.txt          # Analysis report (convert to PDF for submission)
└── models/
    ├── mnist_fc.onnx           # Trained model (generated)
    ├── sample_inputs.npy       # Test samples  (generated)
    └── sample_labels.npy       # Sample labels (generated)
```
