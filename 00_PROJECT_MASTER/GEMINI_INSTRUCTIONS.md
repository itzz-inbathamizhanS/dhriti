# DHṚTI — Gemini Development Instructions

Before writing code:

1. Read `PROJECT_MASTER.md`.
2. Read `01_LITERATURE\LITERATURE_MATRIX.md`.
3. Read `02_BIOLOGY\BIOLOGY_MATRIX.md`.
4. Read `03_QUANTUM\QUANTUM_MATRIX.md`.
5. Read `07_NOVELTY\NOVELTY_ANALYSIS.md`.
6. Read `09_EVIDENCE\SOURCES.md`.
7. Inspect the existing repository structure.
8. Do not delete or overwrite existing research material.

## Research Integrity

Do not:
- invent papers
- invent citations
- invent datasets
- invent experimental results
- claim unverified novelty
- present hypotheses as established facts

## Development Rule

Do not implement the final research contribution until the literature and novelty analysis are complete.

First produce:

- architecture proposal
- module responsibilities
- data flow
- experiment plan
- baseline plan
- testing plan
- risks
- possible overlap with prior work

Then wait for approval before major implementation.

## Coding Requirements

When implementation begins:

- Use Python.
- Keep modules small and testable.
- Write unit tests.
- Use reproducible random seeds.
- Keep raw datasets unchanged.
- Separate research code from production code.
- Record experiment configurations.
- Make CLI functionality installable.
- Document important design decisions.

## Scientific Evaluation

Every claimed improvement must be experimentally measured.

Compare against appropriate baselines.

Include ablation studies.

Report negative results honestly.

Do not optimize the project merely to produce a positive result.

## Primary Objective

Develop DHṚTI as a reproducible research software system investigating:

Whether biologically inspired adaptive repair policies, combined with ML-based repair-strategy selection, can improve the efficiency and/or effectiveness of automated repair of faulty quantum programs.