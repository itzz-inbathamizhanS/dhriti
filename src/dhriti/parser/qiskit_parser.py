"""Qiskit quantum circuit parser.

Converts Qiskit QuantumCircuit objects into DHṚTI's CircuitIR
for downstream fault analysis and repair.
"""

from __future__ import annotations

from pathlib import Path
from typing import Union

from qiskit.circuit import QuantumCircuit
from qiskit.qasm2 import loads as qasm2_loads

from dhriti.core.circuit_ir import CircuitIR


def parse_circuit(source: Union[QuantumCircuit, str, Path]) -> CircuitIR:
    """Parse a quantum circuit from various sources into CircuitIR.

    Args:
        source: A Qiskit QuantumCircuit, a QASM string, or a path
                to a .qasm file.

    Returns:
        CircuitIR: The parsed circuit with extracted metadata.

    Raises:
        ValueError: If the source type is not supported.
    """
    if isinstance(source, QuantumCircuit):
        return CircuitIR.from_circuit(source)
    elif isinstance(source, Path) or (isinstance(source, str) and source.endswith(".qasm")):
        path = Path(source)
        qasm_str = path.read_text()
        circuit = qasm2_loads(qasm_str)
        return CircuitIR.from_circuit(circuit)
    elif isinstance(source, str):
        # Try as QASM string
        circuit = qasm2_loads(source)
        return CircuitIR.from_circuit(circuit)
    else:
        raise ValueError(f"Unsupported source type: {type(source)}")
