"""DHRITI Command-Line Interface.

An installable developer tool for automated quantum program repair
with ML-based repair operator selection.

Usage:
    dhriti analyze <circuit.qasm>    Analyze a quantum circuit
    dhriti diagnose <circuit.qasm>   Detect and localize faults
    dhriti repair <circuit.qasm>     Repair a faulty circuit
    dhriti benchmark                 Run benchmark experiments
    dhriti train                     Train the ML selector
    dhriti version                   Show version info
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Optional

from dhriti import __version__
from dhriti.core.config import DhritiConfig


def cmd_analyze(args: argparse.Namespace) -> None:
    """Analyze a quantum circuit: parse and extract features."""
    from dhriti.parser.qiskit_parser import parse_circuit
    from qiskit.qasm2 import load as qasm2_load

    circuit_path = Path(args.circuit)
    if not circuit_path.exists():
        print(f"Error: File not found: {circuit_path}")
        sys.exit(1)

    print(f"Analyzing: {circuit_path}")

    circuit = qasm2_load(str(circuit_path))
    ir = parse_circuit(circuit)

    print(f"\nCircuit Summary:")
    print(f"  Qubits:       {ir.num_qubits}")
    print(f"  Depth:        {ir.depth}")
    print(f"  Total gates:  {ir.total_gate_count}")
    print(f"  Gate types:   {ir.gate_type_counts}")
    print(f"  Parameters:   {ir.parameter_count}")
    print(f"  Measurements: {ir.measurement_count}")

    print(f"\nGate List ({len(ir.gate_list)} gates):")
    for i, g in enumerate(ir.gate_list):
        flags = []
        if g.is_parameterized:
            flags.append("param")
        if g.is_controlled:
            flags.append("ctrl")
        if g.is_entangling:
            flags.append("ent")
        flag_str = f" [{', '.join(flags)}]" if flags else ""
        print(f"  [{i:3d}] {g.name:<6} qubits={g.qubits} depth={g.depth_layer}{flag_str}")


def cmd_diagnose(args: argparse.Namespace) -> None:
    """Detect and localize faults in a quantum circuit."""
    from dhriti.parser.qiskit_parser import parse_circuit
    from dhriti.detection.oracle import TestOracle
    from dhriti.localization.spectrum import SpectrumLocalizer
    from dhriti.characterization.features import extract_features
    from dhriti.core.fault import FaultDescriptor
    from qiskit.qasm2 import load as qasm2_load

    config = DhritiConfig(simulator_shots=args.shots)

    circuit_path = Path(args.circuit)
    if not circuit_path.exists():
        print(f"Error: File not found: {circuit_path}")
        sys.exit(1)

    print(f"Diagnosing: {circuit_path}")

    circuit = qasm2_load(str(circuit_path))
    ir = parse_circuit(circuit)

    # If reference circuit provided, use it for comparison
    if args.reference:
        ref_path = Path(args.reference)
        ref_circuit = qasm2_load(str(ref_path))
        oracle = TestOracle(config=config)
        expected = oracle.run_circuit(ref_circuit)

        result = oracle.compare(circuit, expected)
        print(f"\nFault Detection:")
        print(f"  Is faulty:    {result.is_faulty}")
        print(f"  Fidelity:     {result.fidelity:.4f}")
        print(f"  KL divergence: {result.kl_divergence:.4f}")

        if result.is_faulty:
            print(f"\nFault Localization (top-{args.top_k}):")
            localizer = SpectrumLocalizer(config=config)
            susp_result = localizer.localize(ir, expected)
            top_suspects = localizer.get_top_suspects(susp_result, k=args.top_k)

            for rank, (gate_idx, score) in enumerate(top_suspects, 1):
                if gate_idx < len(ir.gate_list):
                    gate = ir.gate_list[gate_idx]
                    print(f"  #{rank}: gate[{gate_idx}] {gate.name} "
                          f"qubits={gate.qubits} score={score:.4f}")
    else:
        print("\nNote: Provide --reference <correct.qasm> for fault detection.")
        print("Without a reference, only analysis is available.")
        cmd_analyze(args)


def cmd_repair(args: argparse.Namespace) -> None:
    """Attempt to repair a faulty quantum circuit."""
    from dhriti.parser.qiskit_parser import parse_circuit
    from dhriti.detection.oracle import TestOracle
    from dhriti.localization.spectrum import SpectrumLocalizer
    from dhriti.core.fault import FaultDescriptor
    from dhriti.repair.generator import RepairGenerator
    from dhriti.verification.validator import RepairValidator
    from dhriti.selection.ml_selector import MLRepairSelector
    from dhriti.selection.pathway_selector import PathwaySelector
    from dhriti.selection.baselines import RandomSelector
    from qiskit.qasm2 import load as qasm2_load

    config = DhritiConfig(
        simulator_shots=args.shots,
        max_repair_attempts=args.max_attempts,
        top_k_locations=args.top_k,
    )

    circuit_path = Path(args.circuit)
    if not circuit_path.exists():
        print(f"Error: File not found: {circuit_path}")
        sys.exit(1)

    if not args.reference:
        print("Error: --reference <correct.qasm> is required for repair.")
        sys.exit(1)

    ref_path = Path(args.reference)
    if not ref_path.exists():
        print(f"Error: Reference not found: {ref_path}")
        sys.exit(1)

    print(f"Repairing: {circuit_path}")
    print(f"Reference: {ref_path}")

    circuit = qasm2_load(str(circuit_path))
    ref_circuit = qasm2_load(str(ref_path))
    ir = parse_circuit(circuit)

    # Get expected distribution
    oracle = TestOracle(config=config)
    expected = oracle.run_circuit(ref_circuit)

    # Detect fault
    det_result = oracle.compare(circuit, expected)
    print(f"\nFault detected: {det_result.is_faulty} (fidelity={det_result.fidelity:.4f})")

    if not det_result.is_faulty:
        print("Circuit appears correct. No repair needed.")
        return

    # Localize
    localizer = SpectrumLocalizer(config=config)
    susp_result = localizer.localize(ir, expected)
    suspects = localizer.get_top_suspects(susp_result, k=args.top_k)

    # Select strategy
    if args.selector == "ml":
        model_path = Path(args.model) if args.model else Path("experiments/ml_model.joblib")
        if model_path.exists():
            selector = MLRepairSelector()
            selector.load(model_path)
            print(f"Using ML selector (loaded from {model_path})")
        else:
            print(f"Warning: Model not found at {model_path}. Using pathway selector.")
            selector = PathwaySelector()
    elif args.selector == "pathway":
        selector = PathwaySelector()
        print("Using bio-pathway selector")
    else:
        selector = RandomSelector()
        print("Using random selector")

    # Generate repairs
    fault_desc = FaultDescriptor(output_deviation=1.0 - det_result.fidelity)
    generator = RepairGenerator(selector=selector, config=config)
    gen_result = generator.generate(circuit, ir, suspects, fault_desc)

    print(f"\nGenerated {len(gen_result.candidates)} candidates "
          f"from {gen_result.total_generated} attempts")

    # Validate
    if gen_result.candidates:
        validator = RepairValidator(config=config)
        outcomes = validator.validate_and_rank(gen_result.candidates, expected)

        successful = [o for o in outcomes if o.success]
        print(f"Successful repairs: {len(successful)}/{len(outcomes)}")

        if successful:
            best = successful[0]
            print(f"\nBest repair:")
            print(f"  Operator:  {best.candidate.operator.value}")
            print(f"  Gate:      {best.candidate.target_gate_index}")
            print(f"  Fidelity:  {best.fidelity:.4f}")
            print(f"  Confidence: {best.candidate.confidence:.4f}")

            if args.output:
                from qiskit.qasm2 import dumps
                repaired_circuit = gen_result.candidates[0][0]
                output_path = Path(args.output)
                output_path.write_text(dumps(repaired_circuit))
                print(f"\nRepaired circuit saved to: {output_path}")
        else:
            print("\nNo successful repair found.")
            if outcomes:
                best = outcomes[0]
                print(f"  Best attempt: {best.candidate.operator.value}, "
                      f"fidelity={best.fidelity:.4f}")
    else:
        print("No candidates could be generated.")


def cmd_benchmark(args: argparse.Namespace) -> None:
    """Run benchmark experiments."""
    if args.kfold:
        from experiments.run_kfold import run_kfold_experiment
        run_kfold_experiment(k=args.folds)
    else:
        from experiments.run_experiment import main as run_main
        run_main()


def cmd_train(args: argparse.Namespace) -> None:
    """Train the ML selector on generated data."""
    from dhriti.core.config import DhritiConfig
    from dhriti.benchmark.dataset import generate_dataset, split_dataset
    from dhriti.benchmark.experiment import _records_to_features_labels
    from dhriti.selection.ml_selector import MLRepairSelector

    config = DhritiConfig(
        random_seed=args.seed,
        numpy_seed=args.seed,
        simulator_shots=2048,
        ml_n_estimators=args.estimators,
    )
    config.seed_all()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    print("Generating training data...")
    records = generate_dataset(
        config=config,
        min_qubits=args.min_qubits,
        max_qubits=args.max_qubits,
        circuits_per_config=3,
        mutations_per_circuit=7,
        verbose=True,
    )

    features, labels = _records_to_features_labels(records)

    print(f"\nTraining ML selector ({args.estimators} estimators)...")
    selector = MLRepairSelector(
        n_estimators=args.estimators,
        random_state=args.seed,
    )
    metrics = selector.train(features, labels)
    print(f"Training metrics: {metrics}")

    model_path = output_dir / "ml_model.joblib"
    selector.save(model_path)
    print(f"Model saved to: {model_path}")


def cmd_version(args: argparse.Namespace) -> None:
    """Show version info."""
    print(f"DHRITI v{__version__}")
    print("Bio-inspired adaptive repair framework for quantum programs")
    print("Primary contribution: ML-based repair operator selection")


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="dhriti",
        description="DHRITI: Bio-inspired adaptive repair framework for quantum programs",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # analyze
    p_analyze = subparsers.add_parser("analyze", help="Analyze a quantum circuit")
    p_analyze.add_argument("circuit", help="Path to QASM file")
    p_analyze.set_defaults(func=cmd_analyze)

    # diagnose
    p_diag = subparsers.add_parser("diagnose", help="Detect and localize faults")
    p_diag.add_argument("circuit", help="Path to QASM file")
    p_diag.add_argument("--reference", "-r", help="Path to correct reference circuit")
    p_diag.add_argument("--shots", type=int, default=4096, help="Simulator shots")
    p_diag.add_argument("--top-k", type=int, default=5, help="Top-k suspect gates")
    p_diag.set_defaults(func=cmd_diagnose)

    # repair
    p_repair = subparsers.add_parser("repair", help="Repair a faulty circuit")
    p_repair.add_argument("circuit", help="Path to faulty QASM file")
    p_repair.add_argument("--reference", "-r", required=True, help="Path to correct circuit")
    p_repair.add_argument("--output", "-o", help="Save repaired circuit to file")
    p_repair.add_argument("--selector", choices=["ml", "pathway", "random"], default="ml")
    p_repair.add_argument("--model", help="Path to trained ML model")
    p_repair.add_argument("--shots", type=int, default=4096)
    p_repair.add_argument("--max-attempts", type=int, default=100)
    p_repair.add_argument("--top-k", type=int, default=5)
    p_repair.set_defaults(func=cmd_repair)

    # benchmark
    p_bench = subparsers.add_parser("benchmark", help="Run benchmark experiments")
    p_bench.add_argument("--kfold", action="store_true", help="Run k-fold cross-validation")
    p_bench.add_argument("--folds", type=int, default=5, help="Number of folds")
    p_bench.set_defaults(func=cmd_benchmark)

    # train
    p_train = subparsers.add_parser("train", help="Train the ML selector")
    p_train.add_argument("--min-qubits", type=int, default=3)
    p_train.add_argument("--max-qubits", type=int, default=10)
    p_train.add_argument("--estimators", type=int, default=200)
    p_train.add_argument("--seed", type=int, default=42)
    p_train.add_argument("--output-dir", default="experiments")
    p_train.set_defaults(func=cmd_train)

    # version
    p_ver = subparsers.add_parser("version", help="Show version info")
    p_ver.set_defaults(func=cmd_version)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()