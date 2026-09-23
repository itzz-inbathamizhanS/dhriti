"""Fault and repair descriptors for DHṚTI."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class FaultType(Enum):
    """Types of quantum program faults (mutation operators)."""

    MISSING_GATE = "missing_gate"
    EXTRA_GATE = "extra_gate"
    WRONG_GATE = "wrong_gate"
    WRONG_QUBIT = "wrong_qubit"
    WRONG_PARAMETER = "wrong_parameter"
    WRONG_CONTROL = "wrong_control"
    WRONG_TARGET = "wrong_target"
    WRONG_GATE_ORDER = "wrong_gate_order"
    WRONG_MEASUREMENT = "wrong_measurement"
    UNKNOWN = "unknown"


class RepairOperator(Enum):
    """Available repair operators.

    Each operator represents a distinct HOW strategy for fixing a fault.
    The ML selector predicts which operator to apply.
    """

    GATE_REPLACEMENT = "gate_replacement"
    GATE_INSERTION = "gate_insertion"
    GATE_DELETION = "gate_deletion"
    PARAMETER_MODIFICATION = "parameter_modification"
    QUBIT_REASSIGNMENT = "qubit_reassignment"
    CONTROL_TARGET_SWAP = "control_target_swap"
    GATE_ORDER_SWAP = "gate_order_swap"
    MEASUREMENT_CORRECTION = "measurement_correction"


@dataclass
class FaultDescriptor:
    """Describes a detected/suspected fault in a quantum circuit."""

    fault_type: FaultType = FaultType.UNKNOWN
    suspected_gate_index: Optional[int] = None
    suspected_qubit: Optional[int] = None
    suspiciousness_score: float = 0.0
    output_deviation: float = 0.0  # KL divergence or 1 - fidelity


@dataclass
class FaultFeatureVector:
    """Feature vector for ML-based repair operator selection.

    Extracted from circuit structure and fault characterization.
    This is the input to the RepairSelector.
    """

    # Circuit-level features
    num_qubits: int = 0
    circuit_depth: int = 0
    total_gate_count: int = 0
    parameter_count: int = 0
    measurement_count: int = 0

    # Gate-type counts (top gate types)
    cx_count: int = 0
    h_count: int = 0
    x_count: int = 0
    rz_count: int = 0
    ry_count: int = 0
    rx_count: int = 0
    t_count: int = 0
    s_count: int = 0
    other_gate_count: int = 0

    # Local features (at suspected fault location)
    suspect_gate_type_encoded: int = 0  # encoded gate type
    suspect_gate_position: int = 0
    suspect_gate_depth: int = 0
    suspect_num_qubits: int = 0
    local_gate_density: float = 0.0
    has_parameters: bool = False
    is_controlled: bool = False
    is_entangling: bool = False

    # Fault-characterization features
    suspiciousness_score: float = 0.0
    output_deviation: float = 0.0

    def to_array(self) -> list[float]:
        """Convert to flat feature array for ML model input."""
        return [
            float(self.num_qubits),
            float(self.circuit_depth),
            float(self.total_gate_count),
            float(self.parameter_count),
            float(self.measurement_count),
            float(self.cx_count),
            float(self.h_count),
            float(self.x_count),
            float(self.rz_count),
            float(self.ry_count),
            float(self.rx_count),
            float(self.t_count),
            float(self.s_count),
            float(self.other_gate_count),
            float(self.suspect_gate_type_encoded),
            float(self.suspect_gate_position),
            float(self.suspect_gate_depth),
            float(self.suspect_num_qubits),
            float(self.local_gate_density),
            float(self.has_parameters),
            float(self.is_controlled),
            float(self.is_entangling),
            float(self.suspiciousness_score),
            float(self.output_deviation),
        ]

    @staticmethod
    def feature_names() -> list[str]:
        """Return feature names for interpretability."""
        return [
            "num_qubits", "circuit_depth", "total_gate_count",
            "parameter_count", "measurement_count",
            "cx_count", "h_count", "x_count", "rz_count",
            "ry_count", "rx_count", "t_count", "s_count",
            "other_gate_count",
            "suspect_gate_type_encoded", "suspect_gate_position",
            "suspect_gate_depth", "suspect_num_qubits",
            "local_gate_density", "has_parameters",
            "is_controlled", "is_entangling",
            "suspiciousness_score", "output_deviation",
        ]


@dataclass
class RepairCandidate:
    """A candidate repair to apply to a faulty circuit."""

    operator: RepairOperator
    target_gate_index: int
    confidence: float = 0.0
    details: dict = field(default_factory=dict)
    # e.g., {"replacement_gate": "h", "new_param": 1.57}


@dataclass
class RepairOutcome:
    """Result of applying a repair candidate."""

    candidate: RepairCandidate
    success: bool = False
    fidelity: float = 0.0
    distribution_similarity: float = 0.0
    compilation_success: bool = False
    execution_success: bool = False
    passes_tests: bool = False
