Exploration of the Marabou Resources Directory
================================================

Source: https://github.com/NeuralNetworkVerification/Marabou/tree/master/resources

This document surveys the built-in benchmarks and example files provided
with the Marabou neural network verification framework.


1. NEURAL NETWORK MODELS
-------------------------

1.1 nnet/ directory — NNet format (.nnet)
  Marabou's original native format. Each file encodes network weights, biases,
  and input normalization parameters in a plain-text format.

  Sub-folders:
  - acasxu/  : ACAS Xu (Airborne Collision Avoidance System X Unmanned)
                45 networks (ACASXU_experimental_v2a_N_M.nnet, N in 1-5, M in 1-9)
                Architecture: 5 inputs, 6 hidden layers × 50 neurons, 5 outputs
                Task: aircraft advisory system (Clear-of-Conflict, weak/strong left/right)
                Source: Katz et al., 2017 (Reluplex paper)

  - coav/    : CollisionAvoidance benchmarks from the Planet paper
                Small networks for UAV collision avoidance scenarios

  - twin/    : TwinStreams benchmarks from the Planet repository
                Used to test multi-output verification

  - mnist/   : mnist10x10.nnet — a tiny MNIST classifier (10×10 hidden layers)
                Used in the parallelism demo (runMarabou.py)

1.2 onnx/ directory — ONNX format (.onnx)
  Marabou 2.0 uses ONNX as its primary format. Files here include small
  feed-forward networks for testing the ONNX parsing pipeline.

1.3 keras/ directory
  Keras/TensorFlow (.pb or SavedModel) format networks.
  Marabou can parse these via its TensorFlow interface.

1.4 mps/ directory
  Linear programming problem files in MPS format.
  Used for solver-level benchmarks, not DNN verification.

1.5 bnn_queries/ directory
  Binary Neural Network (BNN) verification queries.
  These use {-1, +1} weights and test Marabou's BNN support.


2. PROPERTY FILES
------------------

2.1 properties/acas_property_1.txt
  Safety property P1: "If the intruder is far away and there is no danger,
  the network output should not advise a Strong Right turn."
  Input: x[0] in [55947.691, 60760.0], x[1] in [-3.141592, 3.141592], etc.
  Output: y[0] <= 3.9911256459

2.2 properties/acas_property_2.txt
  Property P2: "If the intruder is far away, output 0 (COC) should be maximal."

2.3 properties/acas_property_3.txt
  Property P3: "COC is not the minimal advisory for a specific input region."

2.4 properties/acas_property_4.txt
  Property P4: "The network should not output COC for a specific dangerous scenario."

2.5 properties/builtin_property.txt
  A generic collision avoidance property embedded in the final network layer,
  used for coav/ and twin/ benchmarks.

2.6 properties/mnist/ directory
  MNIST-specific property files, e.g.:
    image3_target6_epsilon0.05.txt
  Format: sets L-inf bounds on all 784 pixel inputs around a reference image
  and constrains the output to match the true class.


3. EXAMPLE SCRIPTS AND NOTEBOOKS
----------------------------------

3.1 runMarabou.py
  Command-line runner script that demonstrates:
  - Loading a .nnet model
  - Loading a property file
  - Running with multiple workers (parallelism)
  Usage example from README:
    ./resources/runMarabou.py resources/nnet/mnist/mnist10x10.nnet \
      resources/properties/mnist/image3_target6_epsilon0.05.txt --num-workers=4

3.2 SplitAndConquerGuide.ipynb
  A Jupyter Notebook walkthrough of the Split-and-Conquer (SNC) mode.
  SNC decomposes a hard verification query into 2^n sub-problems solved
  in parallel, which can dramatically reduce wall-clock time on large queries.

3.3 fashion.ipq
  A serialized Marabou internal query (.ipq format) for a Fashion-MNIST network.
  Can be loaded directly into Marabou without going through ONNX/nnet parsing.


4. SUMMARY TABLE
-----------------

Category          | Files/Formats          | Notes
------------------+------------------------+-----------------------------------
Network formats   | .nnet, .onnx, .pb      | ONNX is the primary format in v2.0
Benchmark suites  | ACAS Xu, coav, twin,   | ACAS Xu is the canonical benchmark
                  | MNIST, Fashion-MNIST   |
Property format   | .txt (custom syntax)   | Line-by-line input/output bounds
                  | .vnnlib               | VNN-COMP standard format supported
Example scripts   | runMarabou.py, .ipynb  | Shows parallel + SNC usage
Serialized query  | .ipq                   | Marabou internal format


5. KEY OBSERVATIONS FOR MODEL SELECTION (Problem 2)
-----------------------------------------------------

- The ACAS Xu .nnet networks are small (5-in, 5-out, 50 neurons/layer) but
  the 45 pre-loaded networks are already part of the resources directory.

- The mnist10x10.nnet is also already included.

- For Problem 2, a model NOT in this directory is required.
  Recommended: train a custom MNIST FC network in PyTorch and export to .onnx.
  The ONNX format is Marabou 2.0's primary supported format and allows
  straightforward use of the Python API (Marabou.read_onnx()).
