# DHṚTI Novelty Analysis

## Current Hypothesis

DHṚTI investigates whether biological repair mechanisms can be converted into an adaptive computational repair policy for faulty quantum programs, with ML selecting or prioritizing repair strategies.

This is a hypothesis, not a novelty claim.

---

## Prior-Art Questions

### A. Quantum Program Repair

- Has automated quantum program repair already been implemented?
  **YES** — UnitAR (2024), HornBro (2024), QRep (2026), LLM-based (2024-2026)

- What repair operators are used?
  **Gate replacement, insertion, deletion, parameter tuning, unitary patch synthesis**

- How are faults localized?
  **Suspiciousness scoring (QRep), stabilizer+Z3 (HornBro), mutation analysis (Mutation-LLM), LLM reasoning**

- How are candidate repairs generated?
  **Algebraic (UnitAR), synthesis (HornBro), prioritized search (QRep), LLM generation**

- How are repairs verified?
  **Test suite execution, simulation, distribution comparison**

### B. Machine Learning

- Has ML been used to select quantum repair strategies?
  **PARTIALLY** — LLMs implicitly select strategies; no dedicated trained ML model for quantum repair operator selection found

- Has ML been used for quantum fault localization?
  **PARTIALLY** — Mutation-based spectrum analysis; GNN for QEC decoding (not program-level)

- Has ML reduced quantum-program-repair search?
  **YES** — QRep's suspiciousness scoring reduces search; Mutation-LLM's context improves LLM accuracy

- What features are used?
  **Test spectra (QRep), mutation analysis results (Mutation-LLM), bug taxonomy (QBugLM); circuit-structural features NOT used by any system**

### C. Biology-Inspired Computing

- Has DNA repair been converted into a software-repair algorithm?
  **NOT DIRECTLY** — GenProg uses evolutionary metaphors (mutation/crossover) but not DNA repair pathway selection

- Has immune-system adaptation been used for software repair?
  **YES for self-healing** — Naqvi et al. (2021) MAPE-K immune model; **NOT for program repair specifically**

- Has biological repair-pathway selection been computationally modeled?
  **NOT FOUND** — No published work converting damage-type-specific pathway selection into a computational algorithm for software repair

- Has adaptive biological repair been used for program repair?
  **NOT FOUND for quantum; GenProg uses evolution for classical**

### D. Combined Area

Search specifically for:

"biologically inspired" + "quantum program repair" → **NOT FOUND**

"DNA repair" + "quantum software" → **NOT FOUND** (only conceptual references in Stepney et al.)

"bio-inspired" + "quantum debugging" → **NOT FOUND**

"biological repair" + "quantum computing" → **NOT FOUND**

"immune-inspired" + "quantum software" → **NOT FOUND**

"adaptive repair" + "quantum program" → **NOT FOUND as bio-inspired; QRep does adaptive search but not bio-inspired**

"machine learning" + "quantum program repair" → **FOUND** — Mutation-LLM uses LLM (a form of ML); no dedicated trained model

---

## Evidence Table (Revised v2)

| Claim | Evidence | Source | Status |
|---|---|---|---|
| Quantum program repair exists | UnitAR, HornBro, QRep, LLM-based, Mutation-LLM | L001-L006 | **CONFIRMED** |
| ML-assisted quantum repair exists | LLM-based repair (Guo et al., Yoshida et al.), QRep scoring | L002, L003, L006 | **CONFIRMED (LLM-based; no dedicated trained model)** |
| Biological software repair exists | GenProg (evolutionary), Naqvi et al. (immune) | L011, B002 | **CONFIRMED (classical only)** |
| DNA-inspired software repair exists | GenProg uses mutation/crossover metaphors | L011 | **CONFIRMED (metaphorical, not pathway selection)** |
| Immune-inspired software repair exists | Naqvi et al. (2021) MAPE-K immune model | B002 | **CONFIRMED (self-healing, not program repair)** |
| Biology-inspired quantum software repair exists | No direct implementation found | Web search | **NOT FOUND (cannot prove negative)** |
| Adaptive repair-policy selection for quantum exists | QRep suspiciousness prioritization; QBugLM iterative retry | L003, L007 | **PARTIALLY EXISTS (not bio-inspired; not ML-learned operator selection)** |
| ML + biological adaptive repair for quantum exists | No evidence found | Web search | **NOT FOUND (cannot prove negative)** |
| Fault-type-aware operator selection exists (classical) | SituRepair (ML fault-type → operator pattern) | L009 | **CONFIRMED (classical C only)** |
| Fault-type-aware repair guidance exists (quantum) | Mutation-LLM (mutation context → LLM); QBugLM (taxonomy → LLM) | L006, L007 | **PARTIALLY EXISTS (via LLM prompting, not dedicated ML model)** |
| Dedicated ML model for quantum repair operator selection exists | No evidence found | Web search | **NOT FOUND (cannot prove negative)** |
| Bandit/RL for quantum APR operator selection exists | No evidence found; exists for classical APR | Web search | **NOT FOUND (cannot prove negative)** |

---

## Possible Contribution (Revised v2)

Do not finalize until the QRep and Mutation-LLM full papers are read.

Potential contribution:

A dedicated, interpretable ML model trained on circuit-structural features (gate types, qubit connectivity, depth, local gate density, parameterization) and fault-characterization features that predicts which repair operator to apply for faulty quantum programs, optionally structured as a biologically inspired multi-pathway triage mechanism.

This is distinct from:
- QRep: which prioritizes WHERE, not which operator
- Mutation-LLM: which uses LLM reasoning with mutation context, not a dedicated trained model
- QBugLM: which uses LLM with taxonomy classification, not a dedicated trained model
- SituRepair: which does this for classical C, not quantum

This may NOT be distinct from:
- QRep if full paper shows it also learns operator selection
- Concurrent 2026 work not yet found
- A reviewer who considers LLM-based repair as already achieving "fault-type-aware operator selection"

---

## Novelty Standard

A statement such as:

"To the best of our systematic literature search..."

is acceptable only after performing and documenting the search.

Never claim:

"Nobody has ever done this."

unless there is extraordinary evidence supporting such a statement.

---

## Decision (Revised v2)

[x] More literature research required (read full QRep and Mutation-LLM papers)

[ ] Original idea appears sufficiently distinct

[x] Existing work requires modification to the research contribution

[ ] Idea substantially overlaps with existing work