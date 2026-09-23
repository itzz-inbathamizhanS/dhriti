# DHṚTI: Learning to Repair Quantum Programs with Adaptive Operator Selection

## Abstract

Automated program repair (APR) for quantum circuits is a nascent field. Existing methods typically rely on random mutation, predefined biological heuristics, or static template matching, failing to leverage the topological and functional characteristics of the buggy circuit. In this paper, we present DHṚTI (धृति), a novel end-to-end quantum program repair framework that employs Machine Learning (ML) to dynamically select the most appropriate repair operator for a localized fault. DHṚTI extracts a 24-dimensional Fault Feature Vector from the circuit's intermediate representation (IR), capturing both local gate topology and output deviation. We evaluate DHṚTI on a diverse dataset of 1,131 mutated quantum circuits (3-15 qubits) and real-world semantic bugs from the Bugs4Q dataset. Our ML-based selector (Random Forest) achieves a 59.9% top-1 accuracy in selecting the correct repair operator, outperforming biological pathway triage (17.4%) and random selection (11.7%) by over 42 percentage points. Furthermore, DHṚTI reduces the search cost of repair generation by 61.1% compared to random baselines and successfully repaired 75% (3 out of 4) of evaluated real-world semantic quantum bugs.

## 1. Introduction

Quantum computing programs are highly susceptible to subtle logic errors. A single misplaced gate or incorrect rotation parameter can drastically alter the final probability distribution of the circuit. Traditional classical Automated Program Repair (APR) techniques rely on Abstract Syntax Trees (ASTs) and execution traces, which do not translate well to the entangled, probabilistic nature of quantum circuits. 

Recent work in quantum APR has explored evolutionary algorithms and predefined biological heuristics to guide the repair process. However, these methods often treat the repair selection as a static probability distribution or rely on rigid pathway triage, ignoring the structural context of the specific fault. 

We introduce DHṚTI, a lightweight, installable developer tool that formulates quantum repair operator selection as a machine learning classification problem. By extracting a rich set of topological and fault-specific features (the *Fault Feature Vector*), DHṚTI learns which repair operators (e.g., gate insertion, deletion, replacement, parameter modification) are statistically most likely to resolve specific classes of quantum bugs.

## 2. Approach

DHṚTI implements a complete repair pipeline:
1. **Fault Detection:** Utilizes a test oracle based on Bhattacharyya fidelity and Kullback-Leibler (KL) divergence to compare the buggy circuit against a reference specification.
2. **Fault Localization:** Adapts Spectrum-Based Fault Localization (SBFL) to quantum circuits via gate-removal mutants, producing a ranked list of suspicious gates.
3. **Feature Extraction:** Constructs a 24-dimensional feature vector for the target gate, capturing `circuit_depth`, `local_gate_density`, `output_deviation`, `control_qubits`, and surrounding gate frequencies.
4. **Adaptive Selection:** An ML model (Random Forest) predicts the optimal repair operator from a set of 8 distinct operators.
5. **Generation & Verification:** Generates candidate circuits and validates them against the test oracle, returning the highest-fidelity repair.

## 3. Evaluation

We conducted extensive evaluations to answer the following Research Questions (RQs):
- **RQ1 (Accuracy):** How accurate is the ML selector compared to baselines?
- **RQ2 (Efficiency):** Does ML selection reduce the search cost of generating valid repairs?
- **RQ3 (Real-World Applicability):** Can DHṚTI repair real-world semantic bugs?

### 3.1 Experimental Setup
We generated a dataset of 1,131 synthetic circuits spanning 6 algorithmic families (QFT, QAOA, VQE, GHZ, W-State, Random) scaled from 3 to 15 qubits. The dataset was seeded with 6 types of single-fault mutations. We performed 5-fold stratified cross-validation.

### 3.2 Results

**RQ1: Accuracy and RQ2: Efficiency**
The ML selector drastically outperformed all baselines.

| Strategy | Top-1 Accuracy | Top-3 Accuracy | Avg Rank |
|----------|----------------|----------------|----------|
| Random | 11.7% ± 1.0% | 35.0% | 4.58 |
| Frequency | 20.4% ± 0.1% | 62.0% | 2.97 |
| Bio-Pathway | 17.4% ± 2.4% | 42.2% | 4.01 |
| **ML Selector (Ours)** | **59.9% ± 4.0%** | **89.2%** | **1.78** |

DHṚTI's ML selector yielded a **61.1% reduction in search cost**, requiring significantly fewer candidate evaluations to find a valid repair.

**Feature Importance Analysis:** The most predictive features were the suspect gate's position (10.6%), output deviation (10.1%), total circuit depth (9.6%), and local gate density (8.3%).

**RQ3: Bugs4Q Real-World Evaluation**
We evaluated DHṚTI on 4 modernized semantic bugs from the historical Bugs4Q dataset. DHṚTI successfully repaired 3 out of 4 (75%) of the bugs:
- **Bug 1 (Wrong gate):** Successfully replaced an erroneous Hadamard gate with an X gate.
- **Bug 3 (Missing gate):** Successfully inserted a missing Hadamard gate to complete an IQFT circuit.
- **Bug 4 (Phase shift):** Discovered a "quantum self-healing" repair by inserting an additional H gate next to an erroneous H gate, leveraging the $H \times H = I$ algebraic identity to perfectly cancel the bug.

### 3.3 Limitations of SBFL in Quantum Circuits
A key finding from our real-world evaluation is the limitation of traditional SBFL for quantum circuits. For highly entangled gates, deleting the faulty gate can cause the output distribution to diverge further from the target than leaving the faulty gate in place. Consequently, SBFL sometimes assigns a suspiciousness score of 0.0 to the actual faulty gate. DHṚTI mitigates this by applying the ML selector to a `top-k` window of suspects rather than strictly the top-1.

## 4. Conclusion
DHṚTI demonstrates that Machine Learning can effectively map the topological features of a quantum circuit to successful repair strategies. By replacing static heuristics with an adaptive ML selector, DHṚTI significantly improves repair accuracy and search efficiency, providing a robust, non-LLM alternative for automated quantum program repair.

---
*Draft prepared for submission.*
