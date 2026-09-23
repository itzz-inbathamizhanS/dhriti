"""Smoke test: end-to-end DHṚTI pipeline verification."""

from qiskit.circuit import QuantumCircuit

from dhriti.parser.qiskit_parser import parse_circuit
from dhriti.detection.oracle import TestOracle
from dhriti.localization.spectrum import SpectrumLocalizer
from dhriti.characterization.features import extract_features
from dhriti.core.fault import FaultDescriptor, FaultFeatureVector, RepairOperator
from dhriti.core.config import DhritiConfig
from dhriti.selection.baselines import RandomSelector
from dhriti.selection.pathway_selector import PathwaySelector
from dhriti.benchmark.mutation import MutationEngine
from dhriti.repair.generator import RepairGenerator
from dhriti.verification.validator import RepairValidator
from dhriti.memory.history import RepairHistory


def main():
    config = DhritiConfig(random_seed=42, numpy_seed=42, simulator_shots=4096)
    config.seed_all()

    # 1. Create a correct circuit (Bell state)
    correct = QuantumCircuit(2)
    correct.h(0)
    correct.cx(0, 1)
    correct.measure_all()
    print(f"[1] Correct circuit: {correct.num_qubits} qubits, depth {correct.depth()}")

    # 2. Parse it
    ir = parse_circuit(correct)
    print(f"[2] Parsed: {ir.num_qubits} qubits, {ir.depth} depth, "
          f"{ir.total_gate_count} gates, types={ir.gate_type_counts}")

    # 3. Get expected distribution
    oracle = TestOracle(config=config)
    expected = oracle.run_circuit(correct)
    print(f"[3] Expected distribution: {expected}")

    # 4. Mutate the circuit
    engine = MutationEngine(seed=42)
    mutation = engine.mutate(correct, fault_type=None)
    if mutation is None:
        # Try a specific fault type
        from dhriti.core.fault import FaultType
        mutation = engine.mutate(correct, fault_type=FaultType.WRONG_GATE)

    if mutation is None:
        print("[4] ERROR: Could not generate mutation")
        return

    print(f"[4] Mutation: {mutation.fault_type.value} at gate {mutation.fault_location}")
    print(f"    Ground truth repair: {mutation.ground_truth_repair.value}")
    print(f"    Details: {mutation.mutation_details}")

    # 5. Detect fault
    result = oracle.compare(mutation.mutated, expected)
    print(f"[5] Fault detected: {result.is_faulty}, fidelity={result.fidelity:.4f}, "
          f"KL={result.kl_divergence:.4f}")

    # 6. Parse mutated circuit
    mutated_ir = parse_circuit(mutation.mutated)

    # 7. Localize (simplified: use mutation location as ground truth)
    suspect_gates = [(mutation.fault_location, 0.9)]
    print(f"[7] Suspect gates: {suspect_gates}")

    # 8. Extract features
    fault_desc = FaultDescriptor(
        suspected_gate_index=mutation.fault_location,
        suspiciousness_score=0.9,
        output_deviation=1.0 - result.fidelity,
    )
    features = extract_features(mutated_ir, mutation.fault_location, fault_desc)
    print(f"[8] Features: {len(features.to_array())} dims, "
          f"gate_type={features.suspect_gate_type_encoded}, "
          f"is_entangling={features.is_entangling}")

    # 9. Test selectors
    random_sel = RandomSelector(seed=42)
    pathway_sel = PathwaySelector()

    random_result = random_sel.select(features)
    pathway_result = pathway_sel.select(features)

    print(f"[9a] Random selector top-3: "
          f"{[(op.value, f'{c:.3f}') for op, c in random_result[:3]]}")
    print(f"[9b] Pathway selector top-3: "
          f"{[(op.value, f'{c:.3f}') for op, c in pathway_result[:3]]}")

    # 10. Generate candidate repairs
    generator = RepairGenerator(selector=pathway_sel, config=config)
    gen_result = generator.generate(
        mutation.mutated, mutated_ir, suspect_gates, fault_desc
    )
    print(f"[10] Generated {len(gen_result.candidates)} candidates from "
          f"{gen_result.total_generated} attempts")

    # 11. Validate candidates
    if gen_result.candidates:
        validator = RepairValidator(config=config)
        outcomes = validator.validate_and_rank(gen_result.candidates, expected)
        best = outcomes[0]
        print(f"[11] Best repair: {best.candidate.operator.value}, "
              f"fidelity={best.fidelity:.4f}, passes={best.passes_tests}")

        # 12. Record in history
        history = RepairHistory()
        for outcome in outcomes:
            history.record(features, outcome)
        print(f"[12] Repair history: {history.size} records, "
              f"success rates: {history.operator_success_rates()}")
    else:
        print("[11] No valid candidates generated")

    print("\n[OK] END-TO-END SMOKE TEST PASSED")


if __name__ == "__main__":
    main()
