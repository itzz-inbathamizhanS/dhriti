"""Circuit intermediate representation for DHṚTI.

Wraps Qiskit's QuantumCircuit and DAGCircuit to provide a unified
representation for fault analysis, feature extraction, and repair.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from qiskit.circuit import QuantumCircuit
from qiskit.dagcircuit import DAGCircuit
from qiskit.converters import circuit_to_dag, dag_to_circuit


@dataclass
class GateInfo:
    """Metadata for a single gate in the circuit."""

    name: str
    qubits: list[int]
    params: list[float]
    depth_layer: int
    position: int  # index in topological order
    is_parameterized: bool = False
    is_controlled: bool = False
    is_entangling: bool = False

    @property
    def num_qubits(self) -> int:
        return len(self.qubits)


@dataclass
class CircuitIR:
    """Intermediate representation of a quantum circuit.

    Provides both the high-level QuantumCircuit and the DAG
    representation, along with extracted structural metadata.
    """

    circuit: QuantumCircuit
    dag: DAGCircuit
    num_qubits: int
    depth: int
    gate_list: list[GateInfo] = field(default_factory=list)
    gate_type_counts: dict[str, int] = field(default_factory=dict)
    total_gate_count: int = 0
    parameter_count: int = 0
    measurement_count: int = 0

    @classmethod
    def from_circuit(cls, circuit: QuantumCircuit) -> CircuitIR:
        """Create CircuitIR from a Qiskit QuantumCircuit."""
        dag = circuit_to_dag(circuit)
        gate_list = []
        gate_type_counts: dict[str, int] = {}
        parameter_count = 0
        measurement_count = 0

        for position, node in enumerate(dag.topological_op_nodes()):
            qubit_indices = [circuit.qubits.index(q) for q in node.qargs]
            params = [float(p) for p in node.op.params] if node.op.params else []
            is_param = len(params) > 0
            is_controlled = node.op.name.startswith("c") and len(qubit_indices) > 1
            is_entangling = len(qubit_indices) > 1

            if node.op.name == "measure":
                measurement_count += 1
                continue

            if node.op.name in ("barrier",):
                continue

            gate_info = GateInfo(
                name=node.op.name,
                qubits=qubit_indices,
                params=params,
                depth_layer=0,  # computed below
                position=position,
                is_parameterized=is_param,
                is_controlled=is_controlled,
                is_entangling=is_entangling,
            )
            gate_list.append(gate_info)
            gate_type_counts[node.op.name] = gate_type_counts.get(node.op.name, 0) + 1
            if is_param:
                parameter_count += len(params)

        # Compute depth layers (simplified: use position-based approximation)
        # A more accurate approach would use the DAG's layer decomposition
        if gate_list:
            layers = list(dag.layers())
            layer_map: dict[int, int] = {}
            for layer_idx, layer in enumerate(layers):
                for node in layer["graph"].op_nodes():
                    # Map by operation identity
                    for g in gate_list:
                        if g.name == node.op.name and g.position not in layer_map:
                            layer_map[g.position] = layer_idx
                            break
            for g in gate_list:
                g.depth_layer = layer_map.get(g.position, 0)

        return cls(
            circuit=circuit,
            dag=dag,
            num_qubits=circuit.num_qubits,
            depth=circuit.depth(),
            gate_list=gate_list,
            gate_type_counts=gate_type_counts,
            total_gate_count=len(gate_list),
            parameter_count=parameter_count,
            measurement_count=measurement_count,
        )

    def to_circuit(self) -> QuantumCircuit:
        """Convert back to a Qiskit QuantumCircuit."""
        return dag_to_circuit(self.dag)
