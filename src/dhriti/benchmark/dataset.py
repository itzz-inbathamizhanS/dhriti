"""Synthetic benchmark dataset generation and management.

Generates a large dataset of (faulty_circuit, features, ground_truth_operator)
triples by:
1. Creating a diverse set of correct quantum circuits (3-15 qubits)
2. Applying controlled mutations to each
3. Extracting FaultFeatureVectors
4. Recording ground-truth repair operators
"""

from __future__ import annotations

import json
import random
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np
from qiskit.circuit import QuantumCircuit
from qiskit.circuit.library import (
    EfficientSU2,
    QFT,
    QuantumVolume,
)

from dhriti.core.circuit_ir import CircuitIR
from dhriti.core.config import DhritiConfig
from dhriti.core.fault import FaultFeatureVector, FaultType, RepairOperator, FaultDescriptor
from dhriti.benchmark.mutation import MutationEngine, MutationResult
from dhriti.characterization.features import extract_features
from dhriti.detection.oracle import TestOracle
from dhriti.parser.qiskit_parser import parse_circuit


@dataclass
class DatasetRecord:
    """A single record in the benchmark dataset."""

    circuit_id: str
    circuit_family: str
    num_qubits: int
    circuit_depth: int
    fault_type: str
    fault_location: int
    ground_truth_repair: str
    features: list[float]
    fidelity_drop: float  # 1 - fidelity(mutated, original)
    mutation_details: dict = field(default_factory=dict)


@dataclass
class DatasetSplit:
    """Train/val/test split of dataset records."""

    train: list[DatasetRecord]
    val: list[DatasetRecord]
    test: list[DatasetRecord]


def _build_bell_state(n_qubits: int) -> QuantumCircuit:
    """Build a GHZ/Bell state circuit."""
    qc = QuantumCircuit(n_qubits)
    qc.h(0)
    for i in range(n_qubits - 1):
        qc.cx(i, i + 1)
    return qc


def _build_superposition(n_qubits: int) -> QuantumCircuit:
    """Build a full superposition circuit."""
    qc = QuantumCircuit(n_qubits)
    for i in range(n_qubits):
        qc.h(i)
    return qc


def _build_entangled_chain(n_qubits: int, rng: random.Random) -> QuantumCircuit:
    """Build a random entangled chain circuit."""
    qc = QuantumCircuit(n_qubits)
    single_gates = ["h", "x", "y", "z", "s", "t"]
    for i in range(n_qubits):
        gate = rng.choice(single_gates)
        getattr(qc, gate)(i)
    for i in range(n_qubits - 1):
        qc.cx(i, i + 1)
    for i in range(n_qubits):
        gate = rng.choice(single_gates)
        getattr(qc, gate)(i)
    return qc


def _build_rotation_circuit(n_qubits: int, rng: random.Random) -> QuantumCircuit:
    """Build a circuit with rotation gates."""
    qc = QuantumCircuit(n_qubits)
    rot_gates = ["rx", "ry", "rz"]
    for i in range(n_qubits):
        gate = rng.choice(rot_gates)
        angle = rng.uniform(0, 2 * np.pi)
        getattr(qc, gate)(angle, i)
    for i in range(0, n_qubits - 1, 2):
        qc.cx(i, i + 1)
    for i in range(n_qubits):
        gate = rng.choice(rot_gates)
        angle = rng.uniform(0, 2 * np.pi)
        getattr(qc, gate)(angle, i)
    return qc


def _build_qft_like(n_qubits: int) -> QuantumCircuit:
    """Build a QFT-like circuit."""
    try:
        qft = QFT(n_qubits)
        return qft.decompose()
    except Exception:
        # Fallback
        return _build_bell_state(n_qubits)


def _build_random_deep(n_qubits: int, rng: random.Random) -> QuantumCircuit:
    """Build a deeper random circuit."""
    qc = QuantumCircuit(n_qubits)
    single_gates = ["h", "x", "y", "z", "s", "t"]
    depth_layers = rng.randint(3, 8)
    for _ in range(depth_layers):
        for i in range(n_qubits):
            gate = rng.choice(single_gates)
            getattr(qc, gate)(i)
        # Add some entanglement
        for i in range(0, n_qubits - 1, 2):
            if rng.random() < 0.7:
                qc.cx(i, i + 1)
    return qc


# All circuit generator functions
CIRCUIT_FAMILIES = {
    "bell_ghz": _build_bell_state,
    "superposition": _build_superposition,
    "entangled_chain": _build_entangled_chain,
    "rotation": _build_rotation_circuit,
    "qft_like": _build_qft_like,
    "random_deep": _build_random_deep,
}

# Families that need an rng parameter
_FAMILIES_WITH_RNG = {"entangled_chain", "rotation", "random_deep"}


def generate_circuit_suite(
    min_qubits: int = 3,
    max_qubits: int = 10,
    circuits_per_config: int = 3,
    seed: int = 42,
) -> list[tuple[str, QuantumCircuit]]:
    """Generate a diverse suite of correct quantum circuits.

    Args:
        min_qubits: Minimum qubit count.
        max_qubits: Maximum qubit count.
        circuits_per_config: Number of circuits per (family, qubit_count).
        seed: Random seed.

    Returns:
        List of (circuit_id, circuit) tuples.
    """
    rng = random.Random(seed)
    circuits = []

    for n_qubits in range(min_qubits, max_qubits + 1):
        for family_name, builder in CIRCUIT_FAMILIES.items():
            for variant in range(circuits_per_config):
                circuit_id = f"{family_name}_q{n_qubits}_v{variant}"
                try:
                    if family_name in _FAMILIES_WITH_RNG:
                        circuit = builder(n_qubits, rng)
                    else:
                        circuit = builder(n_qubits)
                    circuits.append((circuit_id, circuit))
                except Exception:
                    pass  # Skip circuits that can't be built

    return circuits


def generate_dataset(
    config: Optional[DhritiConfig] = None,
    min_qubits: int = 3,
    max_qubits: int = 10,
    circuits_per_config: int = 3,
    mutations_per_circuit: int = 5,
    verbose: bool = True,
) -> list[DatasetRecord]:
    """Generate the full synthetic benchmark dataset.

    Args:
        config: DHRTI configuration.
        min_qubits: Minimum qubit count.
        max_qubits: Maximum qubit count.
        circuits_per_config: Circuits per (family, qubits).
        mutations_per_circuit: Mutations per circuit.
        verbose: Print progress.

    Returns:
        List of DatasetRecord instances.
    """
    config = config or DhritiConfig()
    config.seed_all()

    oracle = TestOracle(config=config)
    engine = MutationEngine(seed=config.random_seed)

    # Generate circuit suite
    circuits = generate_circuit_suite(
        min_qubits=min_qubits,
        max_qubits=max_qubits,
        circuits_per_config=circuits_per_config,
        seed=config.random_seed,
    )

    if verbose:
        print(f"Generated {len(circuits)} correct circuits")

    # Applicable fault types (skip UNKNOWN)
    fault_types = [ft for ft in FaultType if ft != FaultType.UNKNOWN]

    records: list[DatasetRecord] = []
    errors = 0

    for idx, (circuit_id, circuit) in enumerate(circuits):
        if verbose and idx % 20 == 0:
            print(f"  Processing circuit {idx + 1}/{len(circuits)}: {circuit_id}")

        try:
            # Get expected distribution
            expected = oracle.run_circuit(circuit)

            # Parse circuit
            circuit_ir = parse_circuit(circuit)

            # Apply mutations
            for m_idx in range(mutations_per_circuit):
                fault_type = fault_types[m_idx % len(fault_types)]

                try:
                    mutation = engine.mutate(circuit, fault_type=fault_type)
                    if mutation is None:
                        continue

                    # Measure fidelity drop
                    try:
                        mutated_dist = oracle.run_circuit(mutation.mutated)
                        all_keys = set(expected.keys()) | set(mutated_dist.keys())
                        fidelity = sum(
                            np.sqrt(expected.get(k, 0) * mutated_dist.get(k, 0))
                            for k in all_keys
                        )
                        fidelity_drop = 1.0 - fidelity
                    except Exception:
                        fidelity_drop = 1.0  # Assume max drop on error

                    # Parse mutated circuit and extract features
                    mutated_ir = parse_circuit(mutation.mutated)
                    fault_desc = FaultDescriptor(
                        suspected_gate_index=mutation.fault_location,
                        suspiciousness_score=0.9,
                        output_deviation=fidelity_drop,
                    )

                    gate_idx = min(
                        mutation.fault_location,
                        len(mutated_ir.gate_list) - 1
                    )
                    if gate_idx < 0:
                        continue

                    features = extract_features(mutated_ir, gate_idx, fault_desc)

                    record = DatasetRecord(
                        circuit_id=circuit_id,
                        circuit_family=circuit_id.split("_q")[0],
                        num_qubits=circuit.num_qubits,
                        circuit_depth=circuit.depth(),
                        fault_type=mutation.fault_type.value,
                        fault_location=mutation.fault_location,
                        ground_truth_repair=mutation.ground_truth_repair.value,
                        features=features.to_array(),
                        fidelity_drop=float(fidelity_drop),
                        mutation_details=mutation.mutation_details,
                    )
                    records.append(record)

                except Exception:
                    errors += 1

        except Exception:
            errors += 1

    if verbose:
        print(f"Dataset: {len(records)} records, {errors} errors")
        # Show distribution
        from collections import Counter
        repair_dist = Counter(r.ground_truth_repair for r in records)
        print(f"Repair distribution: {dict(repair_dist)}")
        fault_dist = Counter(r.fault_type for r in records)
        print(f"Fault distribution: {dict(fault_dist)}")

    return records


def split_dataset(
    records: list[DatasetRecord],
    train_ratio: float = 0.7,
    val_ratio: float = 0.15,
    seed: int = 42,
) -> DatasetSplit:
    """Split dataset into train/val/test sets.

    Uses stratified splitting to maintain repair operator distribution.
    """
    rng = random.Random(seed)

    # Group by ground_truth_repair for stratification
    from collections import defaultdict
    by_repair: dict[str, list[DatasetRecord]] = defaultdict(list)
    for r in records:
        by_repair[r.ground_truth_repair].append(r)

    train, val, test = [], [], []

    for repair_type, group in by_repair.items():
        rng.shuffle(group)
        n = len(group)
        n_train = max(1, int(n * train_ratio))
        n_val = max(1, int(n * val_ratio))

        train.extend(group[:n_train])
        val.extend(group[n_train:n_train + n_val])
        test.extend(group[n_train + n_val:])

    rng.shuffle(train)
    rng.shuffle(val)
    rng.shuffle(test)

    return DatasetSplit(train=train, val=val, test=test)


def save_dataset(records: list[DatasetRecord], path: Path) -> None:
    """Save dataset to JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    data = [asdict(r) for r in records]
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def load_dataset(path: Path) -> list[DatasetRecord]:
    """Load dataset from JSON."""
    with open(path) as f:
        data = json.load(f)
    return [DatasetRecord(**d) for d in data]
