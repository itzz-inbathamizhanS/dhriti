"""Bugs4Q Real-World Evaluation.

Evaluates DHṚTI on modernized QASM versions of 4 real-world semantic bugs
extracted and adapted from the Bugs4Q dataset.
"""

import json
from pathlib import Path

from qiskit import QuantumCircuit
from qiskit.qasm2 import dumps

from dhriti.core.config import DhritiConfig
from dhriti.parser.qiskit_parser import parse_circuit
from dhriti.detection.oracle import TestOracle
from dhriti.localization.spectrum import SpectrumLocalizer
from dhriti.core.fault import FaultDescriptor
from dhriti.repair.generator import RepairGenerator
from dhriti.selection.ml_selector import MLRepairSelector
from dhriti.verification.validator import RepairValidator


BUGS = {
    "bug_1_wrong_gate": {
        "source": "stackoverflow-6-10/bug_2",
        "description": "User wanted to entangle qubits but applied H to both before CX.",
        "buggy_qasm": """OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
creg c[2];
h q[0];
h q[1];
cx q[0], q[1];
measure q[0] -> c[0];
measure q[1] -> c[1];
""",
        "fixed_qasm": """OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
creg c[2];
h q[0];
x q[1];
cx q[0], q[1];
measure q[0] -> c[0];
measure q[1] -> c[1];
""",
    },
    "bug_2_control_target_swap": {
        "source": "StackExchange/14 (adapted)",
        "description": "Control and target qubits flipped in CX gate.",
        "buggy_qasm": """OPENQASM 2.0;
include "qelib1.inc";
qreg q[3];
creg c[3];
h q[0];
cx q[1], q[0];
cx q[2], q[1];
measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];
""",
        "fixed_qasm": """OPENQASM 2.0;
include "qelib1.inc";
qreg q[3];
creg c[3];
h q[0];
cx q[0], q[1];
cx q[1], q[2];
measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];
""",
    },
    "bug_3_missing_gate": {
        "source": "stackoverflow-6-10/bug_3 (adapted 2-qubit QFT)",
        "description": "Missing the final Hadamard gate in QFT.",
        "buggy_qasm": """OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
creg c[2];
h q[0];
cu1(pi/2) q[1], q[0];
measure q[0] -> c[0];
measure q[1] -> c[1];
""",
        "fixed_qasm": """OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
creg c[2];
h q[0];
cu1(pi/2) q[1], q[0];
h q[1];
measure q[0] -> c[0];
measure q[1] -> c[1];
""",
    },
    "bug_4_extra_gate": {
        "source": "Terra-4001-6000/Bug_5 (adapted)",
        "description": "Erroneous extra gate causing unexpected phase shift.",
        "buggy_qasm": """OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
creg c[2];
h q[0];
h q[1];
h q[0];
cx q[0], q[1];
measure q[0] -> c[0];
measure q[1] -> c[1];
""",
        "fixed_qasm": """OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
creg c[2];
h q[0];
h q[1];
cx q[0], q[1];
measure q[0] -> c[0];
measure q[1] -> c[1];
""",
    }
}


def main():
    print("=" * 60)
    print("DHRITI - Bugs4Q Real-World Evaluation")
    print("=" * 60)

    config = DhritiConfig(
        random_seed=42,
        simulator_shots=4096,
        top_k_locations=5,
        max_repair_attempts=500,
    )
    config.seed_all()

    # Load trained ML model
    model_path = Path("experiments/ml_model.joblib")
    if not model_path.exists():
        print(f"Error: Trained model not found at {model_path}")
        return

    selector = MLRepairSelector()
    selector.load(model_path)
    print(f"Loaded ML selector from {model_path}\n")

    oracle = TestOracle(config=config)
    localizer = SpectrumLocalizer(config=config)
    validator = RepairValidator(config=config)

    results = []

    for bug_name, bug_info in BUGS.items():
        print("-" * 60)
        print(f"Evaluating: {bug_name}")
        print(f"Source: {bug_info['source']}")
        print(f"Desc: {bug_info['description']}")
        
        # Load circuits
        from qiskit.qasm2 import loads
        buggy_qc = loads(bug_info["buggy_qasm"])
        fixed_qc = loads(bug_info["fixed_qasm"])

        # 1. Oracle
        expected_dist = oracle.run_circuit(fixed_qc)
        det_result = oracle.compare(buggy_qc, expected_dist)
        print(f"\n[1] Detection:")
        print(f"    Is faulty: {det_result.is_faulty}")
        print(f"    Fidelity:  {det_result.fidelity:.4f}")

        if not det_result.is_faulty:
            print("    Skipping (not faulty).")
            continue

        # 2. Localization
        buggy_ir = parse_circuit(buggy_qc)
        susp_result = localizer.localize(buggy_ir, expected_dist)
        top_suspects = localizer.get_top_suspects(susp_result, k=config.top_k_locations)
        print(f"\n[2] Localization (top-3):")
        for rank, (idx, score) in enumerate(top_suspects[:3], 1):
            gate = buggy_ir.gate_list[idx] if idx < len(buggy_ir.gate_list) else None
            g_name = gate.name if gate else "Unknown"
            print(f"    #{rank}: gate[{idx}] {g_name} (score={score:.4f})")

        # 3. Repair Generation
        print(f"\n[3] Repair Generation (using ML selector):")
        fault_desc = FaultDescriptor(output_deviation=1.0 - det_result.fidelity)
        generator = RepairGenerator(selector=selector, config=config)
        gen_result = generator.generate(buggy_qc, buggy_ir, top_suspects, fault_desc)
        print(f"    Generated {len(gen_result.candidates)} candidates")

        # 4. Validation
        print(f"\n[4] Validation:")
        if not gen_result.candidates:
            print("    FAIL: No candidates generated.")
            results.append({"bug": bug_name, "success": False, "reason": "no_candidates"})
            continue

        outcomes = validator.validate_and_rank(gen_result.candidates, expected_dist)
        successful = [o for o in outcomes if o.success]

        if successful:
            best = successful[0]
            print(f"    SUCCESS! Found {len(successful)} valid repairs.")
            print(f"    Best repair:")
            print(f"      Operator: {best.candidate.operator.value}")
            print(f"      Target:   gate[{best.candidate.target_gate_index}]")
            print(f"      Fidelity: {best.fidelity:.4f}")
            
            # Count rank (how many candidates evaluated before finding this one)
            # Find the original rank in the generated candidates list
            original_rank = 1
            for cand in gen_result.candidates:
                if (cand[1].operator == best.candidate.operator and 
                    cand[1].target_gate_index == best.candidate.target_gate_index):
                    break
                original_rank += 1
                
            results.append({
                "bug": bug_name, 
                "success": True, 
                "operator": best.candidate.operator.value,
                "fidelity": float(best.fidelity),
                "search_cost": original_rank
            })
        else:
            print("    FAIL: No successful repair found.")
            if outcomes:
                print(f"    Best attempt fidelity: {outcomes[0].fidelity:.4f}")
            results.append({"bug": bug_name, "success": False, "reason": "no_valid_repair"})

    # Summary
    print("\n" + "=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)
    success_count = sum(1 for r in results if r["success"])
    print(f"Total Bugs:      {len(BUGS)}")
    print(f"Repaired:        {success_count}")
    print(f"Success Rate:    {success_count / len(BUGS):.1%}")
    
    if success_count > 0:
        avg_cost = sum(r.get("search_cost", 0) for r in results if r["success"]) / success_count
        print(f"Avg Search Cost: {avg_cost:.1f} candidates evaluated")
        
    # Save results
    out_path = Path("experiments/bugs4q_results.json")
    out_path.parent.mkdir(exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {out_path}")

if __name__ == "__main__":
    main()
