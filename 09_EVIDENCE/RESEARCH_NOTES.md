# DHṚTI Research Notes

## Known Facts

- Automated quantum program repair is an active field with at least 5 systems: UnitAR (2024), HornBro (2024), QRep (2026), LLM-based (Guo 2024, Yoshida 2026), QBugLM (2026)
- QRep achieves 70% full repair on circuits up to 13 qubits using suspiciousness-based gate prioritization
- Mutation-analysis-assisted LLM repair achieves 94.4% success rate (Yoshida et al., SANER-ERA 2026)
- QBugLM's iterative feedback boosts Pass@1 from <25% to >80%
- SituRepair does ML fault-type → operator selection for classical C programs
- MAB-based adaptive operator selection is established in classical APR
- RepairAgent (ICSE 2025) demonstrates agentic adaptive strategy selection for classical APR
- GenProg is bio-inspired (evolutionary) APR for classical programs
- Naqvi et al. (2021) implements immune-inspired self-healing software (MAPE-K)
- Bugs4Q provides 42 validated Qiskit bugs as benchmark

## Existing Approaches

- **WHERE selection**: QRep (suspiciousness scoring), HornBro (stabilizer+Z3), MQT Debugger (slicing)
- **HOW selection (quantum)**: UnitAR (algebraic unitary patches), HornBro (gate synthesis), LLMs (implicit)
- **Fault-type-aware repair (quantum)**: Mutation-LLM (mutation context → LLM), QBugLM (taxonomy → LLM)
- **Fault-type-aware repair (classical)**: SituRepair (ML → operator patterns)
- **Adaptive/learned selection (classical)**: MAB-APR, RepairAgent, GenProg
- **Bio-inspired APR (classical)**: GenProg (evolution), Naqvi (immune)

## Observed Limitations

- UnitAR: limited to ≤5 qubits
- QRep: operator selection mechanism unknown from abstract; preliminary evaluation
- All quantum repair systems are stateless (no repair-history feedback)
- No quantum APR uses a dedicated ML model trained on circuit-structural features for operator selection
- No quantum APR uses bio-inspired mechanisms
- LLM-based approaches are expensive and non-interpretable
- Bugs4Q has version dependency issues requiring re-validation

## Potential Research Gaps

- **Gap 1**: Dedicated ML model for quantum repair operator selection (not LLM) using circuit-structural features
- **Gap 2**: Bandit/RL-adaptive operator selection for quantum APR (transfer from classical)
- **Gap 3**: Bio-inspired repair pathway selection for any software domain (not just quantum)
- **Gap 4**: Repair-history feedback mechanism in quantum APR (beyond LLM retry)
- **Gap 5**: Circuit-structural feature extraction for quantum repair guidance

Note: All gaps are "not found" claims, not "does not exist" claims.

## Hypotheses

- H1: An ML model trained on circuit-structural features can predict appropriate repair operators more efficiently than exhaustive search
- H2: Biological repair pathway selection provides a meaningful algorithmic structure for operator selection (not just naming)
- H3: Repair-history feedback improves strategy selection for recurring fault patterns
- H4: The quantum domain presents unique challenges (unitary constraints, entanglement features, parameterized gates) that make operator selection non-trivially different from classical

## Questions Requiring Further Investigation

- Q1: Does QRep also select operators or only locations? (requires full paper reading)
- Q2: Does Mutation-LLM's mutation analysis context constitute "fault-type-aware operator selection"?
- Q3: Is a reviewer likely to consider LLM-based implicit operator selection as equivalent to DHṚTI's explicit ML model?
- Q4: Should DHṚTI position against LLM-based repair or as a complementary lightweight alternative?
- Q5: Is the biological inspiration genuinely algorithmic or merely taxonomic naming?
- Q6: What circuit scale should DHṚTI target (5, 13, or configurable)?

## Experimental Findings

- (None yet — Phase 1 research only)

## Important Negative Results

- (None yet — no experiments conducted)