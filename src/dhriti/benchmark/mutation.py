"""Mutation operator framework for benchmark generation.

Systematically introduces faults into correct quantum circuits
to produce the DHṚTI-Synthetic benchmark dataset.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum
from typing import Optional

import numpy as np
from qiskit.circuit import QuantumCircuit
from qiskit.converters import circuit_to_dag, dag_to_circuit

from dhriti.core.fault import FaultType, RepairOperator


@dataclass
class MutationResult:
    """Result of applying a mutation to a circuit."""

    original: QuantumCircuit
    mutated: QuantumCircuit
    fault_type: FaultType
    fault_location: int  # gate index
    ground_truth_repair: RepairOperator
    mutation_details: dict


# Mapping from fault type to the repair that undoes it
FAULT_TO_REPAIR: dict[FaultType, RepairOperator] = {
    FaultType.MISSING_GATE: RepairOperator.GATE_INSERTION,
    FaultType.EXTRA_GATE: RepairOperator.GATE_DELETION,
    FaultType.WRONG_GATE: RepairOperator.GATE_REPLACEMENT,
    FaultType.WRONG_QUBIT: RepairOperator.QUBIT_REASSIGNMENT,
    FaultType.WRONG_PARAMETER: RepairOperator.PARAMETER_MODIFICATION,
    FaultType.WRONG_CONTROL: RepairOperator.CONTROL_TARGET_SWAP,
    FaultType.WRONG_TARGET: RepairOperator.CONTROL_TARGET_SWAP,
    FaultType.WRONG_GATE_ORDER: RepairOperator.GATE_ORDER_SWAP,
    FaultType.WRONG_MEASUREMENT: RepairOperator.MEASUREMENT_CORRECTION,
}


class MutationEngine:
    """Generates faulty quantum circuits via controlled mutations.

    Each mutation corresponds to a specific FaultType and has a
    known ground-truth repair operator.
    """

    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self.np_rng = np.random.RandomState(seed)

    def mutate(
        self,
        circuit: QuantumCircuit,
        fault_type: Optional[FaultType] = None,
    ) -> Optional[MutationResult]:
        """Apply a single mutation to a circuit.

        Args:
            circuit: The correct circuit to mutate.
            fault_type: Specific fault type to inject.
                If None, a random type is chosen.

        Returns:
            MutationResult with the mutated circuit and metadata,
            or None if mutation was not applicable.
        """
        if fault_type is None:
            fault_type = self.rng.choice(list(FaultType))
            if fault_type == FaultType.UNKNOWN:
                fault_type = FaultType.WRONG_GATE

        dag = circuit_to_dag(circuit)
        op_nodes = [
            n for n in dag.topological_op_nodes()
            if n.op.name not in ("barrier", "measure")
        ]

        if not op_nodes:
            return None

        if fault_type == FaultType.WRONG_GATE:
            return self._wrong_gate(circuit, op_nodes)
        elif fault_type == FaultType.MISSING_GATE:
            return self._missing_gate(circuit, op_nodes)
        elif fault_type == FaultType.EXTRA_GATE:
            return self._extra_gate(circuit)
        elif fault_type == FaultType.WRONG_PARAMETER:
            return self._wrong_parameter(circuit, op_nodes)
        elif fault_type == FaultType.WRONG_QUBIT:
            return self._wrong_qubit(circuit, op_nodes)
        elif fault_type == FaultType.WRONG_CONTROL:
            return self._wrong_control(circuit, op_nodes)
        elif fault_type == FaultType.WRONG_GATE_ORDER:
            return self._wrong_gate_order(circuit, op_nodes)
        else:
            return None

    def _wrong_gate(self, circuit, op_nodes):
        """Replace a gate with a different gate of the same arity."""
        target_idx = self.rng.randrange(len(op_nodes))
        target = op_nodes[target_idx]
        n_qubits = len(target.qargs)

        single_gates = ["h", "x", "y", "z", "s", "t"]
        two_gates = ["cx", "cz", "swap"]

        dag = circuit_to_dag(circuit)
        dag.remove_op_node(list(dag.topological_op_nodes())[
            [i for i, n in enumerate(dag.topological_op_nodes())
             if n.op.name not in ("barrier", "measure")][target_idx]
        ])

        mutated = dag_to_circuit(dag)
        qubits_indices = [circuit.qubits.index(q) for q in target.qargs]

        if n_qubits == 1:
            candidates = [g for g in single_gates if g != target.op.name]
            new_gate = self.rng.choice(candidates) if candidates else "x"
            getattr(mutated, new_gate)(mutated.qubits[qubits_indices[0]])
        elif n_qubits == 2:
            candidates = [g for g in two_gates if g != target.op.name]
            new_gate = self.rng.choice(candidates) if candidates else "cx"
            getattr(mutated, new_gate)(
                mutated.qubits[qubits_indices[0]],
                mutated.qubits[qubits_indices[1]],
            )
        else:
            return None

        return MutationResult(
            original=circuit,
            mutated=mutated,
            fault_type=FaultType.WRONG_GATE,
            fault_location=target_idx,
            ground_truth_repair=RepairOperator.GATE_REPLACEMENT,
            mutation_details={
                "original_gate": target.op.name,
                "replacement_gate": new_gate,
            },
        )

    def _missing_gate(self, circuit, op_nodes):
        """Remove a gate to simulate a missing gate fault."""
        target_idx = self.rng.randrange(len(op_nodes))

        dag = circuit_to_dag(circuit)
        non_meta = [n for n in dag.topological_op_nodes()
                    if n.op.name not in ("barrier", "measure")]
        dag.remove_op_node(non_meta[target_idx])

        return MutationResult(
            original=circuit,
            mutated=dag_to_circuit(dag),
            fault_type=FaultType.MISSING_GATE,
            fault_location=target_idx,
            ground_truth_repair=RepairOperator.GATE_INSERTION,
            mutation_details={"removed_gate": op_nodes[target_idx].op.name},
        )

    def _extra_gate(self, circuit):
        """Insert a random gate to simulate an extra gate fault."""
        qubit = self.rng.randrange(circuit.num_qubits)
        gate = self.rng.choice(["h", "x", "y", "z", "s", "t"])

        mutated = circuit.copy()
        getattr(mutated, gate)(mutated.qubits[qubit])

        return MutationResult(
            original=circuit,
            mutated=mutated,
            fault_type=FaultType.EXTRA_GATE,
            fault_location=circuit.size(),  # appended at end
            ground_truth_repair=RepairOperator.GATE_DELETION,
            mutation_details={"added_gate": gate, "qubit": qubit},
        )

    def _wrong_parameter(self, circuit, op_nodes):
        """Modify a parameter of a parameterized gate."""
        param_nodes = [
            (i, n) for i, n in enumerate(op_nodes)
            if n.op.params
        ]
        if not param_nodes:
            return None

        target_idx, target = self.rng.choice(param_nodes)
        old_param = float(target.op.params[0])
        new_param = old_param + self.np_rng.uniform(0.1, np.pi)

        dag = circuit_to_dag(circuit)
        non_meta = [n for n in dag.topological_op_nodes()
                    if n.op.name not in ("barrier", "measure")]

        from qiskit.circuit.library import RXGate, RYGate, RZGate
        gate_map = {"rx": RXGate, "ry": RYGate, "rz": RZGate}

        if target.op.name in gate_map:
            new_op = gate_map[target.op.name](new_param)
            dag.substitute_node(non_meta[target_idx], new_op)
        else:
            return None

        return MutationResult(
            original=circuit,
            mutated=dag_to_circuit(dag),
            fault_type=FaultType.WRONG_PARAMETER,
            fault_location=target_idx,
            ground_truth_repair=RepairOperator.PARAMETER_MODIFICATION,
            mutation_details={
                "gate": target.op.name,
                "old_param": old_param,
                "new_param": float(new_param),
            },
        )

    def _wrong_qubit(self, circuit, op_nodes):
        """Change the qubit of a single-qubit gate."""
        single_nodes = [
            (i, n) for i, n in enumerate(op_nodes)
            if len(n.qargs) == 1
        ]
        if not single_nodes or circuit.num_qubits < 2:
            return None

        target_idx, target = self.rng.choice(single_nodes)
        old_qubit = circuit.qubits.index(target.qargs[0])
        new_qubit = self.rng.choice(
            [q for q in range(circuit.num_qubits) if q != old_qubit]
        )

        dag = circuit_to_dag(circuit)
        non_meta = [n for n in dag.topological_op_nodes()
                    if n.op.name not in ("barrier", "measure")]
        dag.remove_op_node(non_meta[target_idx])
        mutated = dag_to_circuit(dag)

        if hasattr(mutated, target.op.name):
            if target.op.params:
                getattr(mutated, target.op.name)(
                    *[float(p) for p in target.op.params],
                    mutated.qubits[new_qubit],
                )
            else:
                getattr(mutated, target.op.name)(mutated.qubits[new_qubit])

        return MutationResult(
            original=circuit,
            mutated=mutated,
            fault_type=FaultType.WRONG_QUBIT,
            fault_location=target_idx,
            ground_truth_repair=RepairOperator.QUBIT_REASSIGNMENT,
            mutation_details={
                "gate": target.op.name,
                "old_qubit": old_qubit,
                "new_qubit": new_qubit,
            },
        )

    def _wrong_control(self, circuit, op_nodes):
        """Swap control and target of a controlled gate."""
        controlled = [
            (i, n) for i, n in enumerate(op_nodes)
            if len(n.qargs) == 2 and n.op.name.startswith("c")
        ]
        if not controlled:
            return None

        target_idx, target = self.rng.choice(controlled)
        q0 = circuit.qubits.index(target.qargs[0])
        q1 = circuit.qubits.index(target.qargs[1])

        dag = circuit_to_dag(circuit)
        non_meta = [n for n in dag.topological_op_nodes()
                    if n.op.name not in ("barrier", "measure")]
        dag.remove_op_node(non_meta[target_idx])
        mutated = dag_to_circuit(dag)

        # Add back with swapped control/target
        if hasattr(mutated, target.op.name):
            getattr(mutated, target.op.name)(
                mutated.qubits[q1], mutated.qubits[q0]
            )

        return MutationResult(
            original=circuit,
            mutated=mutated,
            fault_type=FaultType.WRONG_CONTROL,
            fault_location=target_idx,
            ground_truth_repair=RepairOperator.CONTROL_TARGET_SWAP,
            mutation_details={
                "gate": target.op.name,
                "original_control": q0,
                "original_target": q1,
            },
        )

    def _wrong_gate_order(self, circuit, op_nodes):
        """Swap two adjacent gates on the same qubit."""
        if len(op_nodes) < 2:
            return None

        # Find adjacent gates that share a qubit
        for i in range(len(op_nodes) - 1):
            q1 = set(circuit.qubits.index(q) for q in op_nodes[i].qargs)
            q2 = set(circuit.qubits.index(q) for q in op_nodes[i + 1].qargs)
            if q1 & q2:  # shared qubit
                # Simple approach: remove both and add in swapped order
                dag = circuit_to_dag(circuit)
                non_meta = [n for n in dag.topological_op_nodes()
                            if n.op.name not in ("barrier", "measure")]

                if i + 1 >= len(non_meta):
                    continue

                n1 = non_meta[i]
                n2 = non_meta[i + 1]
                dag.remove_op_node(n2)
                dag.remove_op_node(
                    [n for n in dag.topological_op_nodes()
                     if n.op.name not in ("barrier", "measure")][i]
                )

                mutated = dag_to_circuit(dag)

                # Add in reverse order (n2 first, then n1)
                for node in [n2, n1]:
                    qubits = [circuit.qubits.index(q) for q in node.qargs]
                    q_objs = [mutated.qubits[q] for q in qubits]
                    if node.op.params:
                        getattr(mutated, node.op.name)(
                            *[float(p) for p in node.op.params], *q_objs
                        )
                    elif hasattr(mutated, node.op.name):
                        getattr(mutated, node.op.name)(*q_objs)

                return MutationResult(
                    original=circuit,
                    mutated=mutated,
                    fault_type=FaultType.WRONG_GATE_ORDER,
                    fault_location=i,
                    ground_truth_repair=RepairOperator.GATE_ORDER_SWAP,
                    mutation_details={
                        "gate1": n1.op.name,
                        "gate2": n2.op.name,
                        "position": i,
                    },
                )

        return None
