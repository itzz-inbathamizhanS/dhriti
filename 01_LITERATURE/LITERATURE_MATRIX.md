# DHṚTI Literature Matrix

| ID | Paper | Authors | Year | DOI/arXiv | Problem | Method | Dataset | Tool | Results | Limitations | Relation to DHṚTI | Overlap |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| L001 | Automatic Repair of Quantum Programs via Unitary Operation | Yuechen Li; Hanyu Pei; Linzhi Huang; Beibei Yin; Kai-Yuan Cai | 2024 | DOI: 10.1145/3664604 | Automated quantum-program repair | UnitAR; unitary-operation algebraic model; generate-and-validate | 29 mutated + 5 real-world buggy programs | UnitAR | Fixed 23 buggy programs | Scalability ≤5 qubits; single algebraic repair strategy | Direct baseline for DHṚTI; selects HOW (algebraic patch) but not via learned model | HIGH |
| L002 | On Repairing Quantum Programs Using ChatGPT | Xiaoyu Guo; Jianjun Zhao; Pengzhan Zhao | 2024 | DOI: 10.1145/3643667.3648223; arXiv:2401.14913 | LLM-assisted quantum-program repair | ChatGPT-based repair with multi-round prompting | Bugs4Q; 38 bugs evaluated | ChatGPT | Repaired 29/38 reported bugs | Initial exploration; requires human-provided hints | LLM implicitly selects both WHERE and HOW | HIGH |
| L003 | Quantum Circuit Repair by Gate Prioritisation | Eñaut Mendiluze Usandizaga; Thomas Laurent; Paolo Arcaini; Shaukat Ali | 2026 | arXiv:2603.25587; DOI: 10.1109/ICST69053.2026.00095 | Automated quantum-circuit repair and fault localization | QRep; gate suspiciousness scoring; repair prioritization | 40 real/synthetic faulty circuits (≤13 qubits) | QRep | Completely repaired 70%; faulty gate ranked within top 44% for remaining | Preliminary evaluation; operator selection strategy unclear from abstract | Closest competitor; selects WHERE via suspiciousness, operator selection method needs full-paper verification | VERY HIGH |
| L004 | Bugs4Q: A Benchmark of Existing Bugs | Pengzhan Zhao; Zhongtao Miao; Shuhan Lan; Jianjun Zhao | 2023 | DOI: 10.5281/zenodo.8148982 | Benchmarking quantum-program bugs | 42 manually validated Qiskit bugs + tests | Bugs4Q | Provides buggy/fixed programs and reproduction tests | Benchmark depends on software/version context | Primary benchmark candidate | MEDIUM |
| L005 | HornBro — Automated Quantum Program Repair | Unknown (from downloaded papers) | 2024 | Unknown | Automated quantum-program repair | Homotopy-like classical-quantum switching; gate removal + synthesis | Synthetic + real circuits | HornBro | 62.5% improvement in success rate; 35.7× speedup | Unknown | Selects both WHERE (stabilizer+Z3 FL) and HOW (synthesis); formal, not learned | HIGH |
| L006 | Leveraging Mutation Analysis for LLM-based Repair of Quantum Programs | Chihiro Yoshida; Yuta Ishimoto; Olivier Nourry; Masanari Kondo; Makoto Matsushita; Yasutaka Kamei; Yoshiki Higo | 2026 | arXiv:2601.12273; SANER-ERA 2026 | LLM-based quantum repair with mutation analysis context | LLM prompted with static info + stack traces + QMutPy mutation analysis results | Bugs4Q (re-validated) | Framework (not named) | Up to 94.4% repair success rate | ERA paper; mutation analysis adds cost; LLM-dependent | Uses fault characterization (mutation analysis) to guide repair; conceptually close to DHṚTI's fault-characterization pipeline | HIGH |
| L007 | QBugLM: An Agentic Benchmarking Framework for LLM-based Quantum Software Debugging | Unknown | 2026 | arXiv:2606.07314; QSW 2026 | Agentic LLM quantum debugging benchmark | Taxonomy-driven bug injection → LLM detection → LLM repair → simulation validation | OpenQASM 3.0 programs; taxonomy-generated bugs | QBugLM | Pass@1 from <25% to >80% with iterative feedback | Benchmarking framework; relies on LLM capability | Bug-type classification before repair overlaps with DHṚTI's fault characterization → strategy selection | MEDIUM-HIGH |
| L008 | MQT Debugger | TU Munich | 2025-2026 | github.com/munich-quantum-toolkit | Quantum circuit debugging | Circuit slicing + simulation + assertions; IDE integration (VSCode DAP) | N/A (debugging tool) | MQT Debugger | Usability-focused tool | Diagnostic only; no repair capability | Low overlap; diagnostic tool, not repair | LOW |
| L009 | SituRepair | Unknown | Unknown | Unknown | Fault-type-aware automated program repair for C | ML predicts fault type + location → selects situational repair patterns | Code4Bench (C programs) | SituRepair | Outperforms GenProg on multi-fault C programs | Classical only; not quantum | CRITICAL classical precedent: does ML fault-type → operator selection, exactly DHṚTI's core concept but for C | HIGH (conceptual) |
| L010 | RepairAgent | Bouzenia et al. | 2024 | ICSE 2025 | Autonomous LLM-based APR | FSM-guided agentic tool selection; dynamically selects strategies via feedback | Defects4J | RepairAgent | Fixed 164 bugs; outperforms ChatRepair, SelfAPR | Classical Java only; LLM-dependent | Demonstrates adaptive strategy selection in APR is mainstream; reduces DHṚTI's "adaptive policy" novelty | MEDIUM |
| L011 | GenProg | Le Goues et al. | 2012 | Multiple | Search-based APR | Genetic programming: mutation + crossover of program variants | Large C programs | GenProg | Foundational APR paper; multiple test-of-time awards | Classical only; bio-inspiration is evolutionary, not repair-pathway selection | Bio-inspired APR exists (evolutionary biology), but different mechanism from DHṚTI's pathway triage | MEDIUM |

## Required Research Areas

1. Automated quantum program repair
2. Quantum fault localization
3. Quantum debugging
4. Quantum mutation testing
5. Quantum program synthesis
6. ML-assisted quantum software engineering
7. Bio-inspired software repair
8. Biological error detection and repair
9. Adaptive repair systems
10. Bio-inspired optimization for software engineering

## Evidence Rules

- Prefer original research papers.
- Record DOI or arXiv ID whenever available.
- Do not rely on titles alone.
- Read the methodology and evaluation.
- Record actual limitations stated by the authors.
- Mark uncertain information as `Unknown`.
- Never invent missing information.
- Do not claim DHṚTI is novel until overlap has been investigated.