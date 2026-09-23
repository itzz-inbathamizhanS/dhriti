# DHṚTI Biology Literature Matrix

| ID | Paper | Biological Mechanism | Computational Abstraction | Application | Method | Results | Limitations | Relevance to DHṚTI |
|---|---|---|---|---|---|---|---|---|
| B001 | GenProg (Le Goues et al., 2012) | Evolutionary biology: mutation + crossover + selection | Genetic programming; population of program variants evolved via fitness | Automated program repair for C | Generate-and-validate with evolutionary search | Foundational APR; multiple test-of-time awards | Metaphorical use of evolution; no specific repair-pathway selection | Bio-inspired APR exists but uses evolution, not repair-pathway triage |
| B002 | Adaptive Immunity for Software (Naqvi et al., 2021) | Adaptive immune system: self/non-self discrimination, anomaly detection | MAPE-K feedback loop (Monitor, Analyze, Plan, Execute); immune-inspired anomaly detection | Self-healing software | Immune-inspired software self-healing framework | Published at SANER 2021 | Classical software only; not program repair per se; focuses on runtime anomaly detection | Closest bio-inspired software repair precedent; MAPE-K loop is structurally similar to DHṚTI's detect→characterize→select→repair pipeline |
| B003 | A Biologically Inspired Programming Model (George) | Morphogenesis / tissue regeneration / cellular self-repair | Cell-based programming; software built from biological program metaphors | Self-healing software architectures | Conceptual framework | Conceptual | No implementation for program repair; philosophical level | Conceptual inspiration only; no quantum application |
| B004 | Repair Pathway Choices (biology paper) | DNA damage-type-specific repair pathway selection | Multiple repair pathways activated based on damage type: BER for small damage, NER for bulky lesions, HR for double-strand breaks | Biological DNA repair | Biological research | Well-established biological mechanism | Biological mechanism, not computational | PRIMARY biological inspiration for DHṚTI: different fault types → different repair strategies |
| B005 | DNA Mismatch Repair (biology paper) | MutS/MutL mismatch detection → strand discrimination → excision → resynthesis | Mismatch detection → localization → removal → correction pipeline | Biological DNA repair | Biological research | Well-established | Biological mechanism, not computational | Maps to DHṚTI's fault detection → fault localization → repair generation → verification pipeline |
| B006 | Artificial Immune Systems (AIS) literature | Clonal selection, negative selection, immune memory | Meta-heuristic optimization; anomaly detection; immune memory for repeated threats | Intrusion detection, optimization, verification | Multiple AIS algorithms | Established field | Often used for anomaly detection, not repair; no quantum application found | Immune memory maps to DHṚTI's repair-history feedback mechanism |

## Mechanisms to Investigate

- DNA proofreading → Fault detection (mismatch between expected and actual output)
- DNA mismatch repair → Fault localization + targeted correction
- DNA damage detection → Fault characterization
- DNA repair pathway selection → Repair strategy selection (CORE MECHANISM)
- Immune recognition → Anomaly/fault detection
- Adaptive immune response → Strategy adaptation from repair history
- Cellular quality control → Verification of repair correctness
- Evolutionary adaptation → Population-based search (GenProg-style, already done)
- Biological fault tolerance → Graceful degradation

## Required Analysis

For each paper determine:

1. What biological mechanism is used?
2. What computational abstraction is created?
3. What problem does it solve?
4. Has the abstraction already been applied to software repair?
5. Has it been applied specifically to quantum software?
6. What limitation remains?
7. Could the mechanism support DHṚTI without merely renaming an existing technique?

## Key Finding

Biological inspiration in software repair is NOT new (GenProg, AIS, Naqvi et al.).
However:
- Evolutionary biology → APR is well-established (GenProg)
- Immune system → self-healing/anomaly detection is published (Naqvi et al.)
- DNA repair pathway selection → repair operator selection is NOT yet computationally implemented for any software domain
- None of the above have been applied to quantum software

The DHṚTI-specific mechanism (damage-type → pathway selection → operator choice) is biologically distinct from GenProg's evolution metaphor and Naqvi's immune-inspired anomaly detection. However, this must be demonstrated algorithmically, not merely claimed.