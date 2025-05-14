# Knapsack Module Guide

This document explains the structure and usage of the `knapsack.py` module within the `quboin` package. It also provides guidance on testing and using the module through a working example.

---

The `knapsack.py` module provides tools to formulate and solve the **0/1 Knapsack Problem** as a **QUBO** (Quadratic Unconstrained Binary Optimization), enabling it to be solved by quantum annealing or classical samplers.

The module is located at:
```
src/
└── quboin/
└── knapsack.py
```

## 🔍 Contents of `knapsack.py`

### 1. `load_knapsack_data(capacity_file, weights_file, profits_file)`

Parses data files (text files with one number per line) into usable Python data structures for knapsack problems.

**Raises:**

- `ValueError` for empty files, negative capacity, zero/negative weights, and inconsistent lengths.

### 2. `build_knapsack_qubo(weights, profits, capacity, alpha, beta)`

Builds a QUBO dictionary that encodes the standard knapsack problem using a **penalty approach**:

- Variables represent whether an item is included (1) or excluded (0).
- A quadratic penalty is used to enforce the capacity constraint.

Returns a QUBO dictionary that can be passed into `dimod.BinaryQuadraticModel.from_qubo()`.

### 3. `build_knapsack_qubo_aux(weights, profits, capacity, alpha, beta)`

An advanced version using auxiliary variables to encode capacity in binary form. Suitable for more precise or constrained optimization.

## Running Tests

The unit tests are located in the `tests/` directory.

In order to execute all the tests from the project root, use:

```bash
python -m unittest discover -s tests
```

## Example `knapsack_example.py`

This script demonstrates how to use the quboin.knapsack module to solve a knapsack problem using quantum-inspired annealing.

---

### Datasets

Expected in:

```
datasets/
└── knapsack/
    ├── p06_c.txt  ← capacity
    ├── p06_w.txt  ← weights
    ├── p06_p.txt  ← profits
    └── p06_s.txt  ← known optimal solution
```
Each file contains one integer per line.