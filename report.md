Neural Network Verification with Marabou: Local Robustness of an MNIST Classifier
===================================================================================

1. Model, Dataset, and Verification Query
------------------------------------------

Model:
  Architecture : Fully-connected neural network (MLP)
                 Input layer  : 784 neurons (flattened 28×28 MNIST pixels)
                 Hidden layer 1: 64 neurons, ReLU activation
                 Hidden layer 2: 32 neurons, ReLU activation
                 Output layer : 10 neurons (digit classes 0–9)
  Total parameters: ~55,000
  Format : ONNX (opset 11), exported via torch.onnx.export
  Training: 5 epochs on MNIST training set (60,000 images), Adam optimizer,
            cross-entropy loss. Test accuracy: ~97.5%

  Rationale for this model:
  The network is small enough for Marabou's complete SMT-based verifier to
  finish within a reasonable time budget (~5 minutes per query). Larger
  models (e.g., full ResNet) would cause the solver to time out. The ONNX
  format is Marabou 2.0's primary supported format and allows using the
  Python API (maraboupy) directly. MNIST was chosen because it is the
  canonical benchmark for local robustness verification and because ground-
  truth labels are unambiguous.

Dataset:
  MNIST test set (10,000 images). Pixel values are normalized with mean=0.1307
  and std=0.3081, placing them roughly in the range [-2.8, 2.8].

Verification Query (Local Robustness):
  Given a test image x correctly classified as digit d, verify that:

      For ALL x' such that ||x' - x||_inf <= epsilon,
      the network also classifies x' as digit d.

  This is formulated as a SAT problem: Marabou searches for an input x'
  inside the epsilon-ball that causes the network to predict a class j ≠ d.
  - UNSAT means no such x' exists → the network is provably robust.
  - SAT means an adversarial example was found → the property is violated.

  Formally: ∀x' s.t. ‖x' − x‖_∞ ≤ ε  ⟹  argmax f(x') = d

  Input constraints : x'[i] in [x[i] - epsilon, x[i] + epsilon]  for all i
  Output constraints: exists j ≠ d such that output[j] >= output[d]
                      (encoded as a disjunction)


2. Results
-----------

Experiment 1 — Small epsilon (robust case)
  Sample     : Test image index 0, true label = 7
  Epsilon    : 0.01
  Result     : UNSAT
  Runtime    : 0.03 seconds
  Interpretation:
    The network is provably robust within an L-inf ball of
    radius 0.01 around this input. In raw pixel space, ε=0.01 (normalized)
    corresponds to approximately 0.01 × 0.3081 ≈ 0.003 in [0,1] scale,
    or roughly 0.77/255 — less than a single gray-level step. No adversarial
    perturbation of this magnitude can flip the predicted class.

Experiment 2 — Medium epsilon
  Sample     : Test image index 0, true label = 7
  Epsilon    : 0.05
  Result     : UNSAT
  Runtime    : 0.08 seconds
  Interpretation:
    Even with a 5x larger perturbation budget (0.05), Marabou exhaustively searched the space and formally verified that no counterexample exists. The model exhibits high local robustness around this particular sample.

Experiment 3 — Boundary Exploration (Large epsilon)
  Sample     : Test image index 0, true label = 7
  Epsilon    : 0.12 ~ 0.15 (UNSAT) / 0.20 (TIMEOUT)
  Runtime    : ~13s at 0.15 / 300.0s at 0.20
  Interpretation:
    By strictly clamping the perturbation bounds to the valid normalized physical pixel range [-0.42, 2.82], Marabou proved complete robustness (UNSAT) up to epsilon=0.15 in just 13 seconds. Without clamping, the solver previously wasted 248 seconds on epsilon=0.12 and falsely reported SAT at 0.15 by finding "impossible" pixels outside the [0, 255] range. Epsilon 0.20 still resulted in a 300s timeout due to search space explosion.


3. Discussion: Marabou's Strengths and Limitations
----------------------------------------------------

Strengths:
  (a) Formal completeness. Unlike gradient-based attack methods (e.g., FGSM,
      PGD), Marabou provides a formal guarantee. An UNSAT result means the
      property holds for the entire input region — not just for the tested
      samples. This is critical for safety-critical applications.
  (b) Counterexample generation. When a property is violated (SAT), Marabou
      returns a concrete adversarial input, making the failure interpretable
      and actionable.
  (c) Standard format support. Marabou 2.0 accepts ONNX as its primary
      format, which integrates naturally with PyTorch and TensorFlow workflows
      via torch.onnx.export or tf2onnx.
  (d) VNNLIB support. Marabou supports the VNN-COMP property format, enabling
      participation in the standard verification competition benchmark.

Limitations:
  (a) Scalability. The most significant limitation encountered during this
      experiment was computational cost. Even for a small network (784→64→32→
      10) with epsilon=0.01, verification required 0.03 seconds, and pushing epsilon to 0.20 resulted in a hard 300-second timeout. Full-size
      networks (ResNets, VGGs) are currently out of reach for complete
      verification. The number of neurons directly controls the size of the
      LP/SMT problems Marabou must solve. Specifically, Marabou's
      branch-and-bound procedure introduces a binary case-split per ReLU
      neuron (active vs. inactive); with 96 ReLU neurons in this network
      (64 + 32), the worst-case search tree has up to 2^96 leaves, which
      explains the exponential runtime growth observed above ε=0.15.
  (b) Installation complexity. Building Marabou from source on macOS required
      resolving several dependency issues: cmake was not installed by default,
      the download scripts for protobuf and pybind11 did not handle paths with
      spaces correctly, and Boost had to be installed separately via Homebrew.
      These issues add friction that makes Marabou harder to adopt than pip-
      installable tools.
  (c) Supported activation functions. Marabou's complete mode works best with
      piecewise-linear activations (ReLU). Sigmoid, tanh, or GELU activations
      require abstraction-based methods that sacrifice completeness.
  (d) Tight epsilon budgets. For MNIST with normalized inputs, even epsilon=
      0.01 corresponds to a small perturbation in raw pixel space (~2.5/255),
      yet verification still takes significant time. Larger epsilon values may
      cause timeouts on modest hardware.

Personal Observations:
  The experiments highlighted the critical importance of applying Domain Knowledge (Physical Bounds) in formal verification. Without clamping input constraints to valid pixel ranges, the SMT solver wasted massive computational resources exploring impossible inputs—falsely reporting a vulnerability (False SAT) at epsilon=0.15 and taking 248 seconds just to verify epsilon=0.12. By simply enforcing physical pixel limits, the runtime for epsilon=0.12 dropped to 6 seconds (a 40x speedup), and the network was proven perfectly robust (UNSAT) up to 0.15. This concisely demonstrates that optimizing the search space with physical constraints is just as important as the solver's algorithmic power.
  
  Furthermore, from a software engineering perspective, the API transition to Marabou 2.0 (returning a list instead of a tuple, and rearranging the Equation constants) caused minor integration friction, demonstrating that users must be extremely careful with API parsing and updates in safety-critical verification code.
