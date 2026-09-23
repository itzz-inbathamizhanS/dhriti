# DHṚTI Experiment Plan

## Research Question

Does a biologically inspired adaptive repair policy, combined with ML-based repair-strategy selection, improve automated repair of faulty quantum programs?

## RQ1 — Repair Effectiveness

Measure:

- Repair success rate
- Functionally correct repair rate
- Top-1 repair accuracy
- Top-k repair accuracy

## RQ2 — Search Efficiency

Measure:

- Candidate repairs generated
- Simulator executions
- Runtime
- Search-space reduction

## RQ3 — ML Contribution

Compare:

- No ML
- ML-based strategy selection

Measure:

- Precision
- Recall
- F1
- Top-k accuracy

## RQ4 — Biological Adaptive Policy Contribution

Compare:

- Random strategy selection
- Fixed heuristic selection
- Adaptive biological-inspired selection

## RQ5 — Generalization

Test on:

- Unseen circuits
- Unseen fault locations
- Different circuit sizes
- Unseen fault types where feasible

## RQ6 — Ablation

Remove one component at a time:

1. ML
2. Adaptive policy
3. Fault characterization
4. Repair prioritization
5. Candidate ranking

## Baselines

At minimum investigate:

- Exhaustive repair
- Random repair
- Heuristic repair
- Existing quantum-repair approach where reproducible
- ML without biological adaptive policy

## Reproducibility

Record:

- Python version
- Qiskit version
- Dependencies
- Random seeds
- Dataset version
- Hardware
- Experiment configuration
- Execution time

## Important Rule

Do not manufacture positive results.

If the proposed method performs worse than a baseline, report that result honestly and investigate why.