# DHṚTI Dataset Specification

## 1. Raw Data

Never modify the original Bugs4Q dataset.

Location:

04_DATA/Bugs4Q/

---

## 2. DHṚTI Benchmark Record

Each generated benchmark case should contain:

- case_id
- source_program
- faulty_program
- fault_type
- fault_location
- mutation_operator
- ground_truth_repair
- circuit_qubits
- circuit_depth
- gate_count
- gate_type_counts
- parameter_count
- measurement_count
- entanglement-related features where measurable
- expected_output
- verification_result

---

## 3. Fault Types

Initial mutation operators:

- missing_gate
- extra_gate
- wrong_gate
- wrong_qubit
- wrong_parameter
- wrong_control
- wrong_target
- wrong_gate_order
- wrong_measurement

---

## 4. Dataset Splits

Use separate:

- training
- validation
- test

Avoid leakage between splits.

Where possible, test on circuits or bug patterns not seen during training.

---

## 5. ML Features

Potential features:

- circuit depth
- number of qubits
- local gate density
- gate type
- neighboring gates
- qubit index
- parameter presence
- control/target relationships
- fault type
- fault position
- local circuit structure
- previous repair outcomes

Features must be justified experimentally.

---

## 6. Labels

Possible ML targets:

- repair strategy
- candidate repair operator
- repair priority
- candidate location

Do not finalize the target until the literature review determines the strongest research gap.

---

## 7. Data Integrity

For every generated case record:

- source case
- mutation seed
- mutation operator
- mutation location
- generation timestamp
- software/library versions

Experiments must be reproducible.

---

## 8. Evaluation

Never evaluate only on training data.

Report:

- repair success
- functional correctness
- candidate count
- simulator executions
- runtime
- search reduction
- ML metrics
- robustness on unseen cases