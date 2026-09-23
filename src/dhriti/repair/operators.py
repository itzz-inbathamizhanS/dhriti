"""Repair operator implementations.

Each function applies a specific repair operator to a quantum circuit
at a given gate location, producing a modified candidate circuit.
"""

from __future__ import annotations

import random
from typing import Optional

import numpy as np
from qiskit.circuit import QuantumCircuit
from qiskit.converters import circuit_to_dag, dag_to_circuit

from dhriti.core.circuit_ir import CircuitIR, GateInfo
from dhriti.core.fault import RepairCandidate, RepairOperator


# Common single-qubit gates for replacement
SINGLE_QUBIT_GATES = ["h", "x", "y", "z", "s", "t", "sdg", "tdg"]
# Common two-qubit gates for replacement
TWO_QUBIT_GATES = ["cx", "cz", "swap"]
# Common rotation gates
ROTATION_GATES = ["rx", "ry", "rz"]


def apply_repair(
    circuit: QuantumCircuit,
    circuit_ir: CircuitIR,
    candidate: RepairCandidate,
    rng: Optional[random.Random] = None,
) -> Optional[QuantumCircuit]:
    """Apply a repair operator to produce a candidate repaired circuit.

    Args:
        circuit: The faulty circuit.
        circuit_ir: The circuit IR with gate metadata.
        candidate: The repair to apply.
        rng: Random number generator for stochastic operators.

    Returns:
        A new QuantumCircuit with the repair applied, or None on error.
    """
    rng = rng or random.Random(42)

    try:
        op = candidate.operator
        idx = candidate.target_gate_index

        if op == RepairOperator.GATE_REPLACEMENT:
            return _gate_replacement(circuit, circuit_ir, idx, candidate.details, rng)
        elif op == RepairOperator.GATE_DELETION:
            return _gate_deletion(circuit, circuit_ir, idx)
        elif op == RepairOperator.GATE_INSERTION:
            return _gate_insertion(circuit, circuit_ir, idx, candidate.details, rng)
        elif op == RepairOperator.PARAMETER_MODIFICATION:
            return _parameter_modification(circuit, circuit_ir, idx, candidate.details, rng)
        elif op == RepairOperator.QUBIT_REASSIGNMENT:
            return _qubit_reassignment(circuit, circuit_ir, idx, candidate.details, rng)
        elif op == RepairOperator.CONTROL_TARGET_SWAP:
            return _control_target_swap(circuit, circuit_ir, idx)
        elif op == RepairOperator.GATE_ORDER_SWAP:
            return _gate_order_swap(circuit, circuit_ir, idx, candidate.details, rng)
        elif op == RepairOperator.MEASUREMENT_CORRECTION:
            return _measurement_correction(circuit, circuit_ir, idx, candidate.details, rng)
        else:
            return None
    except Exception:
        return None


def _gate_replacement(
    circuit: QuantumCircuit,
    circuit_ir: CircuitIR,
    gate_index: int,
    details: dict,
    rng: random.Random,
) -> Optional[QuantumCircuit]:
    """Replace a gate with another gate of the same arity."""
    if gate_index >= len(circuit_ir.gate_list):
        return None

    gate = circuit_ir.gate_list[gate_index]
    dag = circuit_to_dag(circuit)
    non_meta = [n for n in dag.topological_op_nodes()
                if n.op.name not in ("barrier", "measure")]

    if gate_index >= len(non_meta):
        return None

    target = non_meta[gate_index]
    dag.remove_op_node(target)

    # Select replacement gate
    replacement = details.get("replacement_gate")
    if not replacement:
        if gate.num_qubits == 1:
            candidates = [g for g in SINGLE_QUBIT_GATES + ROTATION_GATES if g != gate.name]
        else:
            candidates = [g for g in TWO_QUBIT_GATES if g != gate.name]
        replacement = rng.choice(candidates) if candidates else gate.name

    # Build the replacement into a new circuit and apply
    new_circuit = dag_to_circuit(dag)
    qubits = [new_circuit.qubits[q] for q in gate.qubits]

    if replacement in ROTATION_GATES:
        param = details.get("new_param", rng.uniform(0, 2 * np.pi))
        getattr(new_circuit, replacement)(param, *qubits)
    elif hasattr(new_circuit, replacement):
        getattr(new_circuit, replacement)(*qubits)

    return new_circuit


def _gate_deletion(
    circuit: QuantumCircuit,
    circuit_ir: CircuitIR,
    gate_index: int,
) -> Optional[QuantumCircuit]:
    """Remove a gate from the circuit."""
    if gate_index >= len(circuit_ir.gate_list):
        return None

    dag = circuit_to_dag(circuit)
    non_meta = [n for n in dag.topological_op_nodes()
                if n.op.name not in ("barrier", "measure")]

    if gate_index >= len(non_meta):
        return None

    dag.remove_op_node(non_meta[gate_index])
    return dag_to_circuit(dag)


def _gate_insertion(
    circuit: QuantumCircuit,
    circuit_ir: CircuitIR,
    gate_index: int,
    details: dict,
    rng: random.Random,
) -> Optional[QuantumCircuit]:
    """Insert a gate at the specified position."""
    gate_to_insert = details.get("insert_gate", rng.choice(SINGLE_QUBIT_GATES))
    qubit = details.get("insert_qubit", rng.randint(0, circuit.num_qubits - 1))

    new_circuit = circuit.copy()
    if hasattr(new_circuit, gate_to_insert):
        getattr(new_circuit, gate_to_insert)(new_circuit.qubits[qubit])
    return new_circuit


def _parameter_modification(
    circuit: QuantumCircuit,
    circuit_ir: CircuitIR,
    gate_index: int,
    details: dict,
    rng: random.Random,
) -> Optional[QuantumCircuit]:
    """Modify the parameter of a parameterized gate."""
    if gate_index >= len(circuit_ir.gate_list):
        return None

    gate = circuit_ir.gate_list[gate_index]
    if not gate.is_parameterized:
        return None

    dag = circuit_to_dag(circuit)
    non_meta = [n for n in dag.topological_op_nodes()
                if n.op.name not in ("barrier", "measure")]

    if gate_index >= len(non_meta):
        return None

    target = non_meta[gate_index]
    new_param = details.get("new_param", rng.uniform(0, 2 * np.pi))

    # Create modified version
    from qiskit.circuit.library import RXGate, RYGate, RZGate
    gate_map = {"rx": RXGate, "ry": RYGate, "rz": RZGate}

    if gate.name in gate_map:
        new_op = gate_map[gate.name](new_param)
        dag.substitute_node(target, new_op)
        return dag_to_circuit(dag)

    return None


def _qubit_reassignment(
    circuit: QuantumCircuit,
    circuit_ir: CircuitIR,
    gate_index: int,
    details: dict,
    rng: random.Random,
) -> Optional[QuantumCircuit]:
    """Change the qubit assignment of a gate."""
    if gate_index >= len(circuit_ir.gate_list):
        return None

    gate = circuit_ir.gate_list[gate_index]
    available = [q for q in range(circuit.num_qubits) if q not in gate.qubits]
    if not available:
        return None

    new_qubit = details.get("new_qubit")
    if new_qubit is None or new_qubit in gate.qubits:
        new_qubit = rng.choice(available)

    dag = circuit_to_dag(circuit)
    non_meta = [n for n in dag.topological_op_nodes()
                if n.op.name not in ("barrier", "measure")]

    if gate_index >= len(non_meta):
        return None

    target = non_meta[gate_index]
    dag.remove_op_node(target)
    new_circuit = dag_to_circuit(dag)

    # Re-add gate on new qubit(s)
    if gate.num_qubits == 1:
        if gate.is_parameterized and gate.params:
            getattr(new_circuit, gate.name)(
                *gate.params, new_circuit.qubits[new_qubit]
            )
        elif hasattr(new_circuit, gate.name):
            getattr(new_circuit, gate.name)(new_circuit.qubits[new_qubit])
    elif gate.num_qubits == 2:
        # Replace one of the two qubits
        old_qubits = list(gate.qubits)
        replace_idx = rng.randint(0, 1)
        old_qubits[replace_idx] = new_qubit
        if hasattr(new_circuit, gate.name):
            getattr(new_circuit, gate.name)(
                new_circuit.qubits[old_qubits[0]],
                new_circuit.qubits[old_qubits[1]],
            )

    return new_circuit


def _control_target_swap(
    circuit: QuantumCircuit,
    circuit_ir: CircuitIR,
    gate_index: int,
) -> Optional[QuantumCircuit]:
    """Swap control and target qubits of a controlled gate."""
    if gate_index >= len(circuit_ir.gate_list):
        return None

    gate = circuit_ir.gate_list[gate_index]
    if not gate.is_controlled or len(gate.qubits) != 2:
        return None

    dag = circuit_to_dag(circuit)
    non_meta = [n for n in dag.topological_op_nodes()
                if n.op.name not in ("barrier", "measure")]

    if gate_index >= len(non_meta):
        return None

    target = non_meta[gate_index]
    dag.remove_op_node(target)

    new_circuit = dag_to_circuit(dag)
    # Add the gate back with swapped qubits
    q0, q1 = gate.qubits[1], gate.qubits[0]  # swapped
    if hasattr(new_circuit, gate.name):
        getattr(new_circuit, gate.name)(
            new_circuit.qubits[q0], new_circuit.qubits[q1]
        )

    return new_circuit


def _gate_order_swap(
    circuit: QuantumCircuit,
    circuit_ir: CircuitIR,
    gate_index: int,
    details: dict,
    rng: random.Random,
) -> Optional[QuantumCircuit]:
    """Swap the order of two adjacent gates."""
    swap_with = details.get("swap_with", gate_index + 1)
    if swap_with >= len(circuit_ir.gate_list) or gate_index >= len(circuit_ir.gate_list):
        return None

    gate_a = circuit_ir.gate_list[gate_index]
    gate_b = circuit_ir.gate_list[swap_with]

    dag = circuit_to_dag(circuit)
    non_meta = [n for n in dag.topological_op_nodes()
                if n.op.name not in ("barrier", "measure")]

    if swap_with >= len(non_meta):
        return None

    # Remove both gates (higher index first to preserve indices)
    hi, lo = max(gate_index, swap_with), min(gate_index, swap_with)
    dag.remove_op_node(non_meta[hi])
    # Re-fetch after removal
    non_meta2 = [n for n in dag.topological_op_nodes()
                 if n.op.name not in ("barrier", "measure")]
    if lo < len(non_meta2):
        dag.remove_op_node(non_meta2[lo])

    new_circuit = dag_to_circuit(dag)

    # Re-add in swapped order (gate_b first, then gate_a)
    for gate in [gate_b, gate_a]:
        q_objs = [new_circuit.qubits[q] for q in gate.qubits]
        if gate.is_parameterized and gate.params:
            getattr(new_circuit, gate.name)(*gate.params, *q_objs)
        elif hasattr(new_circuit, gate.name):
            getattr(new_circuit, gate.name)(*q_objs)

    return new_circuit


def _measurement_correction(
    circuit: QuantumCircuit,
    circuit_ir: CircuitIR,
    gate_index: int,
    details: dict,
    rng: random.Random,
) -> Optional[QuantumCircuit]:
    """Correct measurement operations.

    Strategies:
    - Add missing measurement on a qubit
    - Remove extraneous measurement
    - Reassign measurement to different qubit
    """
    strategy = details.get("strategy", "add")

    if strategy == "add":
        # Add a measurement to a qubit that doesn't have one
        dag = circuit_to_dag(circuit)
        measured_qubits = set()
        for node in dag.topological_op_nodes():
            if node.op.name == "measure":
                measured_qubits.update(
                    circuit.qubits.index(q) for q in node.qargs
                )

        unmeasured = [q for q in range(circuit.num_qubits)
                      if q not in measured_qubits]
        if not unmeasured:
            return None

        qubit = rng.choice(unmeasured)
        new_circuit = circuit.copy()
        from qiskit.circuit import ClassicalRegister
        cr = ClassicalRegister(1, f"repair_c{qubit}")
        new_circuit.add_register(cr)
        new_circuit.measure(new_circuit.qubits[qubit], cr[0])
        return new_circuit

    elif strategy == "remove":
        # Remove a measurement gate
        dag = circuit_to_dag(circuit)
        meas_nodes = [n for n in dag.topological_op_nodes()
                      if n.op.name == "measure"]
        if not meas_nodes:
            return None

        dag.remove_op_node(rng.choice(meas_nodes))
        return dag_to_circuit(dag)

    return None

