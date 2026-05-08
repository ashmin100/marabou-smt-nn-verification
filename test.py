"""
test.py

Runs Marabou verification on a trained MNIST fully-connected network.

Verification query:
  Given an MNIST test image x classified as digit d,
  verify that ALL inputs x' with ||x' - x||_inf <= epsilon
  are also classified as digit d.

  Result:
    UNSAT → the property holds (network is locally robust within epsilon)
    SAT   → a counterexample was found (adversarial input within epsilon-ball)

Usage:
  python test.py [--epsilon FLOAT] [--sample-idx INT] [--timeout INT]

Requirements:
  - Marabou built from source; PYTHONPATH must include the Marabou root directory.
    See README.md for setup instructions.
  - models/mnist_fc.onnx must exist (run train_model.py first).
  - models/sample_inputs.npy and models/sample_labels.npy must exist.
"""

import os
import sys
import time
import argparse
import numpy as np

# ── Argument parsing ──────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Marabou local-robustness verification for MNIST FC")
parser.add_argument("--epsilon",    type=float, default=0.01,
                    help="L-inf perturbation radius (default: 0.01)")
parser.add_argument("--sample-idx", type=int,   default=0,
                    help="Index into saved sample inputs (default: 0)")
parser.add_argument("--timeout",    type=int,   default=300,
                    help="Verification timeout in seconds (default: 300)")
args = parser.parse_args()

# ── Paths ─────────────────────────────────────────────────────────────────────
SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
ONNX_PATH    = os.path.join(SCRIPT_DIR, "models", "mnist_fc.onnx")
SAMPLE_PATH  = os.path.join(SCRIPT_DIR, "models", "sample_inputs.npy")
LABELS_PATH  = os.path.join(SCRIPT_DIR, "models", "sample_labels.npy")

# ── Sanity checks ─────────────────────────────────────────────────────────────
for path in [ONNX_PATH, SAMPLE_PATH, LABELS_PATH]:
    if not os.path.exists(path):
        sys.exit(f"[ERROR] Required file not found: {path}\n"
                 f"        Please run `python train_model.py` first.")

# ── Import Marabou (requires PYTHONPATH to Marabou root) ─────────────────────
try:
    from maraboupy import Marabou, MarabouUtils, MarabouCore
except ImportError:
    sys.exit(
        "[ERROR] Could not import maraboupy.\n"
        "        Make sure PYTHONPATH includes the Marabou root directory.\n"
        "        Example:\n"
        "          export PYTHONPATH=/path/to/Marabou:$PYTHONPATH\n"
        "        See README.md for full setup instructions."
    )

# ── Load sample input ─────────────────────────────────────────────────────────
samples = np.load(SAMPLE_PATH)   # shape: (N, 784), float32, normalized
labels  = np.load(LABELS_PATH)   # shape: (N,),     int64

idx = args.sample_idx
if idx >= len(samples):
    sys.exit(f"[ERROR] sample-idx {idx} out of range (only {len(samples)} samples).")

x       = samples[idx]           # shape (784,)
label   = int(labels[idx])
epsilon = args.epsilon

print("=" * 60)
print("Marabou Local Robustness Verification")
print("=" * 60)
print(f"  Model:       models/mnist_fc.onnx")
print(f"  Sample idx:  {idx}  (true label: {label})")
print(f"  Epsilon:     {epsilon}  (L-inf ball)")
print(f"  Timeout:     {args.timeout}s")
print("=" * 60)

# ── Load network into Marabou ─────────────────────────────────────────────────
print("\n[1/4] Loading ONNX model into Marabou...")
network = Marabou.read_onnx(ONNX_PATH)

# Retrieve input and output variable references
input_vars  = network.inputVars[0].flatten()   # 784 input neurons
output_vars = network.outputVars[0].flatten()  # 10 output neurons

print(f"      Input vars:  {len(input_vars)}")
print(f"      Output vars: {len(output_vars)}")

# ── Set input constraints (L-inf ball around x) ───────────────────────────────
print(f"\n[2/4] Setting input constraints (L-inf ball, epsilon={epsilon})...")

# Pixel values after MNIST normalization are approximately in [-2.8, 2.8].
# We clamp the perturbed bounds to avoid going out of the normalized range.
for i, var in enumerate(input_vars):
    lb = float(x[i]) - epsilon
    ub = float(x[i]) + epsilon
    network.setLowerBound(var, lb)
    network.setUpperBound(var, ub)

print(f"      Bounds set for {len(input_vars)} input neurons.")

# ── Set output constraints (must predict label != true class) ─────────────────
# Marabou looks for a SAT assignment — i.e., an input where the property is VIOLATED.
# Property: output[label] is NOT the maximum output.
# Encoding: exists some class j != label such that output[j] >= output[label].
# We add one disjunction per alternative class.
print(f"\n[3/4] Setting output constraints (violation: any class j≠{label} wins)...")

equations = []
for j in range(10):
    if j == label:
        continue
    # output[j] - output[label] >= 0  →  output[j] >= output[label]
    eq = MarabouUtils.Equation(MarabouCore.Equation.GE)
    eq.addAddend(1, output_vars[j])
    eq.addAddend(-1, output_vars[label])
    eq.setScalar(0)
    equations.append(eq)

# Use disjunction: if ANY of these equations holds, the property is violated
network.addDisjunctionConstraint([[eq] for eq in equations])

print(f"      Added {len(equations)} disjunctive output constraints.")

# ── Run Marabou ───────────────────────────────────────────────────────────────
print(f"\n[4/4] Running Marabou verification...")
options = Marabou.createOptions(timeoutInSeconds=args.timeout, verbosity=0)

t_start = time.time()
result  = network.solve(options=options)
elapsed = time.time() - t_start

# ── Interpret result ──────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("RESULT")
print("=" * 60)
print(f"  Verification time: {elapsed:.2f}s")

# Handle both return-value conventions
if isinstance(result, (list, tuple)) and len(result) == 3:
    exit_code, vals, stats = result
elif isinstance(result, (list, tuple)) and len(result) == 2:
    vals, stats = result
    exit_code = "sat" if len(vals) > 0 else "unsat"
else:
    vals = result
    exit_code = "sat" if (isinstance(vals, dict) and len(vals) > 0) else "unsat"

if exit_code == "unsat" or len(vals) == 0:
    # UNSAT: no counterexample found → property holds
    print(f"  Verdict:  UNSAT")
    print(f"  Meaning:  The network always predicts class {label}")
    print(f"            for all inputs within the L-inf ball of radius {epsilon}.")
    print(f"            The model is locally robust at this sample.")
else:
    # SAT: counterexample found → property violated
    print(f"  Verdict:  SAT (counterexample found)")
    print(f"  Meaning:  An adversarial input exists within the L-inf ball.")

    # Recover the adversarial input vector
    adv_input = np.array([vals[v] for v in input_vars])
    adv_output = np.array([vals[v] for v in output_vars])
    adv_class  = int(np.argmax(adv_output))

    print(f"\n  Adversarial class predicted: {adv_class}  (true: {label})")
    print(f"  Max perturbation (L-inf):    {np.max(np.abs(adv_input - x)):.6f}")
    print(f"  Output logits (adversarial): {np.round(adv_output, 4)}")

print("=" * 60)
