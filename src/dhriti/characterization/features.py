"""Feature extraction for fault characterization.

Extracts circuit-structural and fault-characterization features
from a CircuitIR and a suspected fault location, producing a
FaultFeatureVector for ML-based repair operator selection.
"""

from __future__ import annotations

from typing import Optional

from dhriti.core.circuit_ir import CircuitIR, GateInfo
from dhriti.core.fault import FaultDescriptor, FaultFeatureVector


# Gate type encoding for ML features
GATE_TYPE_ENCODING: dict[str, int] = {
    "h": 1, "x": 2, "y": 3, "z": 4,
    "cx": 5, "cz": 6, "swap": 7,
    "rx": 8, "ry": 9, "rz": 10,
    "t": 11, "s": 12, "tdg": 13, "sdg": 14,
    "ccx": 15, "u": 16, "u1": 17, "u2": 18, "u3": 19,
    "p": 20, "cp": 21, "crx": 22, "cry": 23, "crz": 24,
}


def extract_features(
    circuit_ir: CircuitIR,
    suspect_gate_index: int,
    fault: Optional[FaultDescriptor] = None,
) -> FaultFeatureVector:
    """Extract a feature vector for ML-based operator selection.

    Args:
        circuit_ir: The parsed circuit.
        suspect_gate_index: Index of the suspected faulty gate
            in circuit_ir.gate_list.
        fault: Optional fault descriptor with additional info.

    Returns:
        FaultFeatureVector ready for ML model input.
    """
    features = FaultFeatureVector()

    # Circuit-level features
    features.num_qubits = circuit_ir.num_qubits
    features.circuit_depth = circuit_ir.depth
    features.total_gate_count = circuit_ir.total_gate_count
    features.parameter_count = circuit_ir.parameter_count
    features.measurement_count = circuit_ir.measurement_count

    # Gate-type counts
    counts = circuit_ir.gate_type_counts
    features.cx_count = counts.get("cx", 0)
    features.h_count = counts.get("h", 0)
    features.x_count = counts.get("x", 0)
    features.rz_count = counts.get("rz", 0)
    features.ry_count = counts.get("ry", 0)
    features.rx_count = counts.get("rx", 0)
    features.t_count = counts.get("t", 0)
    features.s_count = counts.get("s", 0)
    known_gates = {"cx", "h", "x", "rz", "ry", "rx", "t", "s"}
    features.other_gate_count = sum(
        v for k, v in counts.items() if k not in known_gates
    )

    # Local features at suspected fault location
    if 0 <= suspect_gate_index < len(circuit_ir.gate_list):
        gate = circuit_ir.gate_list[suspect_gate_index]
        features.suspect_gate_type_encoded = GATE_TYPE_ENCODING.get(gate.name, 0)
        features.suspect_gate_position = gate.position
        features.suspect_gate_depth = gate.depth_layer
        features.suspect_num_qubits = gate.num_qubits
        features.has_parameters = gate.is_parameterized
        features.is_controlled = gate.is_controlled
        features.is_entangling = gate.is_entangling

        # Local gate density: gates within ±2 positions
        window = 2
        start = max(0, suspect_gate_index - window)
        end = min(len(circuit_ir.gate_list), suspect_gate_index + window + 1)
        features.local_gate_density = (end - start) / max(
            1, circuit_ir.total_gate_count
        )

    # Fault-characterization features
    if fault is not None:
        features.suspiciousness_score = fault.suspiciousness_score
        features.output_deviation = fault.output_deviation

    return features
