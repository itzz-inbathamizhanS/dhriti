# DHṚTI Quantum Literature Matrix

| ID | Paper | Year | Quantum Topic | Method | Dataset/Benchmark | Tool | Results | Limitations | Relevance to DHṚTI |
|---|---|---:|---|---|---|---|---|---|---|
| Q001 | UnitAR | 2024 | Quantum program repair | Unitary algebraic repair model; generate-and-validate | 29 mutated + 5 real-world | UnitAR | Fixed 23/34 programs | ≤5 qubits scalability | Direct baseline; single repair strategy |
| Q002 | HornBro | 2024 | Quantum program repair | Homotopy-like switching; gate removal + synthesis; stabilizer+Z3 FL | Synthetic + real circuits | HornBro | 62.5% improvement; 35.7× speedup | Unknown | Formal FL + synthesis; no ML or adaptation |
| Q003 | QRep | 2026 | Quantum circuit repair + fault localization | Gate suspiciousness scoring; prioritized search | 40 circuits (≤13 qubits) | QRep | 70% fully repaired | Preliminary eval; operator selection unclear | CLOSEST competitor; WHERE prioritization, HOW unclear |
| Q004 | Mutation-LLM | 2026 | LLM quantum repair with mutation context | LLM + static/dynamic info + QMutPy mutation analysis | Bugs4Q (re-validated) | Unnamed framework | 94.4% repair rate | ERA paper; LLM-dependent; mutation analysis cost | Fault-characterization-driven repair; conceptually close |
| Q005 | QBugLM | 2026 | Agentic LLM quantum debugging benchmark | Taxonomy-driven bug injection → LLM repair → simulation | OpenQASM 3.0 | QBugLM | Pass@1 <25% → >80% with retry | Benchmark, not repair tool | Bug-type classification before repair |
| Q006 | MQT Debugger | 2025-2026 | Quantum debugging | Circuit slicing + simulation + assertions + IDE | N/A | MQT Debugger | Usability tool | No repair capability | Diagnostic only |
| Q007 | Bugs4Q | 2023 | Quantum bug benchmark | 42 manually validated Qiskit bugs + tests | Bugs4Q | Dataset | Standard benchmark | Version/library dependency issues | Primary benchmark for DHṚTI |
| Q008 | Muskit | 2022 | Quantum mutation testing | Automated mutation analysis for Qiskit | Generated mutants | Muskit | Mutation testing tool | Mutant generation only; no repair | Potential mutant generation source for DHṚTI |
| Q009 | QMutPy | 2022 | Quantum mutation testing | MutPy extension for quantum programs | Generated mutants | QMutPy | Used in Mutation-LLM paper | Extension of classical tool | Alternative mutant generation tool |
| Q010 | Testing and Debugging QP: Road to 2030 | 2025 | Survey / Roadmap | Comprehensive survey of quantum testing/debugging | N/A | N/A | Identifies key gaps and challenges | Survey, not tool | Contextual; identifies standardization gaps |

## Areas

- Quantum program debugging
- Quantum fault localization
- Quantum program repair
- Quantum mutation testing
- Quantum testing
- Quantum program synthesis
- Quantum software engineering
- Quantum circuit optimization
- Quantum error correction
- ML for quantum software

## Required Analysis

For every relevant paper identify:

1. What problem is solved?
2. What algorithm/method is used?
3. What data or benchmark is used?
4. What software/tool is implemented?
5. What are the measurable results?
6. What limitations remain?
7. What part overlaps with DHṚTI?
8. What part does NOT overlap?

## Summary of WHERE vs HOW

| System | Selects WHERE | Selects HOW | Method for HOW |
|--------|:---:|:---:|---|
| UnitAR | Implicitly | Yes | Algebraic unitary patch (single strategy) |
| HornBro | Yes (Z3+stabilizer) | Yes | Gate synthesis (single strategy) |
| QRep | Yes (suspiciousness) | Unknown | Needs full paper verification |
| ChatGPT Repair | Implicitly | Implicitly | LLM generates complete patch |
| Mutation-LLM | Via mutation context | Via mutation context | LLM with enriched prompt |
| QBugLM | Via taxonomy | Via taxonomy | LLM after bug classification |
| DHṚTI (proposed) | Via fault localization | Via ML-trained selector | Dedicated model from circuit features |