# DHṚTI — Project Master Specification

## 1. Project Identity

Project name: DHṚTI

Full name:
Bio-Inspired Adaptive Repair Framework for Automated Quantum Program Debugging and Fault Recovery

Primary domain:
Quantum Computing + Computer Science + Artificial Intelligence + Biology-Inspired Computing

Project type:
Research-oriented software framework and installable developer tool.

Core goal:
Build a real software system that can detect, localize, propose, adapt, and verify repairs for faulty quantum programs.

DHṚTI is NOT intended to be:
- A website-only project
- A simple quantum algorithm demonstration
- A quantum error-correction tutorial
- A generic machine-learning classifier
- A quantum circuit simulator
- A conventional automated quantum program repair system with only a different name
- A claim that biological principles directly improve physical quantum hardware

---

## 2. Central Research Idea

DHṚTI investigates whether biological repair mechanisms can inspire an adaptive computational repair policy for faulty quantum programs.

The biological inspiration should be treated as a computational abstraction.

Examples:

Biological proofreading
→ detect suspicious mismatch

Biological damage localization
→ locate the likely faulty program region

Multiple repair pathways
→ maintain multiple repair strategies

Adaptive repair response
→ select repair strategies according to observed fault characteristics

Repair verification
→ verify whether the repaired system restores intended behavior

The central research question is:

"Can biologically inspired adaptive repair policies, combined with machine-learning-based repair-strategy selection, reduce the search cost of automated quantum-program repair while preserving functional correctness?"

---

## 3. Important Novelty Constraint

Do NOT claim that DHṚTI is the first system to perform automated quantum-program repair.

Existing research already includes automated quantum-program repair and related systems.

Before making any novelty claim, perform a serious literature review.

Relevant existing areas include:
- Quantum program repair
- Automated quantum debugging
- Quantum fault localization
- Quantum program synthesis
- Quantum mutation testing
- Quantum error correction
- Machine-learning-assisted quantum software engineering
- Biology-inspired computing
- Bio-inspired optimization
- Automated program repair

The novelty must be established from evidence.

A possible research contribution to investigate is:

"An adaptive repair-policy framework for quantum-program repair inspired by biological repair mechanisms, where ML selects or prioritizes repair strategies based on fault characteristics."

This is a research hypothesis, NOT an established novelty claim.

---

## 4. Proposed System

Initial conceptual pipeline:

Faulty Quantum Program
        ↓
Quantum Program Parser / Intermediate Representation
        ↓
Fault Detection
        ↓
Fault Localization
        ↓
Fault Characterization
        ↓
Biologically Inspired Adaptive Repair Policy
        ↓
ML-Based Repair Strategy Selection
        ↓
Candidate Repair Generation
        ↓
Quantum Semantic Validation
        ↓
Repair Ranking
        ↓
Verified Repaired Program

The architecture may change after literature review and experiments.

---

## 5. Biological Inspiration

Investigate biological systems that perform reliable repair or adaptation.

Priority concepts:

1. DNA proofreading
2. DNA mismatch repair
3. DNA damage detection
4. DNA repair pathway selection
5. Error correction
6. Immune-system recognition and response
7. Adaptive biological response
8. Evolutionary adaptation
9. Cellular quality-control mechanisms

Do not force biological terminology into the software.

For every biological mechanism used, document:

- Biological mechanism
- Computational abstraction
- Why the abstraction is relevant
- Algorithmic implementation
- Expected benefit
- Experimental test

---

## 6. Quantum Program Scope

Initial supported target should be practical and controlled.

Potential input:
- Qiskit circuits
- OpenQASM where appropriate
- Python-based quantum programs

Initial fault classes may include:

- Missing gate
- Extra gate
- Wrong gate
- Wrong qubit
- Wrong gate parameter
- Wrong control qubit
- Wrong target qubit
- Incorrect gate ordering
- Incorrect measurement
- Incorrect parameter binding

The initial scope should remain manageable.

---

## 7. Machine Learning Role

ML must have a meaningful role.

Possible task:

Given:
- fault characteristics
- circuit structure
- local gate neighborhood
- qubit information
- mutation type
- circuit depth
- gate density
- entanglement-related features
- repair history

predict or prioritize:

- repair strategy
- candidate repair location
- candidate repair operation
- search priority

Do NOT use ML merely to say whether a circuit is "correct" or "incorrect."

---

## 8. Repair Strategies

Potential repair operators:

- Gate replacement
- Gate insertion
- Gate deletion
- Parameter modification
- Qubit reassignment
- Control-target correction
- Gate-order correction
- Measurement correction

The final strategy set must be justified experimentally.

---

## 9. Verification

A repair is not successful merely because the program executes.

Verification should consider:

- Compilation success
- Execution success
- Expected output distribution
- Distribution similarity
- Fidelity or equivalent semantic metric
- Functional correctness
- Regression testing
- Stability across repeated executions where relevant

Define explicit acceptance criteria.

---

## 10. Dataset

Build a controlled benchmark dataset.

Each sample should contain:

- Original correct quantum program
- Fault-free version
- Mutated faulty version
- Fault type
- Fault location
- Mutation details
- Ground-truth repair
- Circuit characteristics
- Verification result

Generate faults systematically so experiments are reproducible.

Avoid relying only on manually created examples.

---

## 11. Experimental Metrics

Measure at minimum:

### Repair performance
- Repair success rate
- Functionally correct repair rate
- Top-1 repair accuracy
- Top-k repair accuracy

### Search efficiency
- Number of candidate patches
- Number of simulator executions
- Search time
- Search-space reduction

### ML performance
- Precision
- Recall
- F1
- Top-k strategy selection accuracy

### Robustness
- Unseen circuits
- Unseen fault locations
- Unseen fault types where possible
- Different circuit sizes

---

## 12. Baselines

Compare DHṚTI against appropriate non-adaptive approaches.

Potential baselines:

- Random repair search
- Exhaustive repair search
- Heuristic repair search
- Existing quantum program repair methods where reproducible
- ML without biological adaptive policy
- Biological adaptive policy without ML

The final baseline selection must be based on the literature and feasibility.

---

## 13. Ablation Studies

Important ablations:

1. No ML
2. No biological adaptive policy
3. No fault characterization
4. Random repair strategy selection
5. Adaptive strategy selection
6. Different feature sets
7. Different repair operators

Goal:

Determine which components actually contribute to performance.

---

## 14. Software Requirements

DHṚTI should become a real installable Python package.

Potential interface:

dhriti analyze <program>

dhriti diagnose <program>

dhriti repair <program>

dhriti verify <program>

dhriti benchmark <directory>

The exact CLI can evolve.

Potential dependencies:

- Python
- Qiskit
- PennyLane where useful
- NumPy
- SciPy
- scikit-learn

Add dependencies only when justified.

---

## 15. Repository Structure

Current repository:

dhriti/

├── 00_PROJECT_MASTER/
├── 01_LITERATURE/
├── 02_BIOLOGY/
├── 03_QUANTUM/
├── 04_DATA/
├── 05_SOFTWARE/
├── 06_EXPERIMENTS/
├── 07_NOVELTY/
├── 08_DOCUMENTATION/
├── 09_EVIDENCE/
│
├── src/
│   └── dhriti/
│
├── tests/
├── datasets/
├── experiments/
├── examples/
├── docs/
├── README.md
├── requirements.txt
└── pyproject.toml

---

## 16. Research Integrity

Never fabricate:

- Papers
- Authors
- Results
- Datasets
- Experiments
- Benchmarks
- Citations
- Novelty claims

Clearly distinguish:

KNOWN:
Established by published evidence.

HYPOTHESIS:
Something DHṚTI proposes to investigate.

EXPERIMENTAL RESULT:
Something demonstrated by DHṚTI experiments.

Do not convert a hypothesis into a fact.

---

## 17. Literature Review Requirements

Create a literature matrix containing:

- Paper title
- Authors
- Year
- DOI / arXiv identifier
- Problem
- Method
- Dataset
- Software/tool
- Evaluation
- Results
- Limitations
- Future work
- Relation to DHṚTI
- Potential overlap with DHṚTI

Prioritize primary research papers.

Search broadly enough to determine whether the proposed contribution has already been implemented.

---

## 18. Novelty Analysis

The novelty investigation must answer:

1. Has biological repair been used for software repair?
2. Has biological repair been used for quantum software repair?
3. Has adaptive repair-policy selection been used for quantum program repair?
4. Has ML selected quantum repair strategies?
5. Has ML + biological repair abstraction been combined for quantum program repair?
6. Are there existing tools implementing substantially the same pipeline?

If substantially similar work exists, modify the research contribution rather than hiding the overlap.

---

## 19. Development Philosophy

Build incrementally.

Phase 1:
Research and novelty validation.

Phase 2:
Quantum program representation.

Phase 3:
Fault generation and benchmark dataset.

Phase 4:
Fault detection and localization.

Phase 5:
Baseline repair engine.

Phase 6:
Biologically inspired adaptive repair policy.

Phase 7:
ML strategy selection.

Phase 8:
Verification and ranking.

Phase 9:
Experiments and ablations.

Phase 10:
Documentation and reproducibility.

Do not implement complex components before establishing the research need for them.

---

## 20. Gemini Instructions

When Gemini is used to develop DHṚTI:

1. Read this entire project specification first.
2. Inspect the existing repository before modifying files.
3. Do not rewrite working components unnecessarily.
4. Do not invent research evidence.
5. Do not claim global novelty without a literature search.
6. Keep research assumptions explicit.
7. Write modular, testable code.
8. Add tests for important functionality.
9. Keep experiments reproducible.
10. Record configuration and random seeds where appropriate.
11. Prefer small validated implementations before large abstractions.
12. Explain major architectural decisions in documentation.
13. Keep the biological inspiration computationally meaningful.
14. Do not add biology terminology merely for presentation.
15. Do not turn DHṚTI into a website-only application.
16. Preserve the project as an installable developer/research tool.
17. When proposing a new component, explain what research question it enables.
18. Before implementing a claimed novel method, check whether substantially similar work exists.
19. Never fabricate citations.
20. Never fabricate experimental results.

---

## 21. Final Research Objective

The final project should demonstrate, with reproducible experiments, whether a biologically inspired adaptive repair policy combined with ML-based repair-strategy selection can improve automated repair of faulty quantum programs compared with appropriate baseline approaches.

The project succeeds scientifically only if the experiments support a defensible conclusion, whether positive, negative, or mixed.