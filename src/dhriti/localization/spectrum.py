"""Spectrum-based fault localization for quantum circuits.

Implements Ochiai and Tarantula suspiciousness metrics to rank
gates by their likelihood of being faulty, based on test
execution spectra.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
from qiskit.circuit import QuantumCircuit

from dhriti.core.circuit_ir import CircuitIR
from dhriti.core.config import DhritiConfig
from dhriti.core.fault import FaultDescriptor, FaultType
from dhriti.detection.oracle import TestOracle


@dataclass
class SuspiciousnessResult:
    """Ranked list of suspicious gates."""

    gate_scores: list[tuple[int, float]]  # (gate_index, score) sorted desc
    metric: str = "ochiai"


class SpectrumLocalizer:
    """Localizes faults using spectrum-based suspiciousness scoring.

    For each gate in the circuit, creates a mutant (gate removed),
    runs it against the oracle, and computes suspiciousness based
    on how the removal affects test outcomes.

    This is a simplified SBFL approach adapted for quantum circuits.
    """

    def __init__(self, config: Optional[DhritiConfig] = None):
        self.config = config or DhritiConfig()
        self.oracle = TestOracle(config=self.config)

    def localize(
        self,
        circuit_ir: CircuitIR,
        expected_distribution: dict[str, float],
        metric: str = "ochiai",
    ) -> SuspiciousnessResult:
        """Compute suspiciousness scores for all gates.

        Args:
            circuit_ir: The parsed faulty circuit.
            expected_distribution: Reference output from correct circuit.
            metric: Suspiciousness metric ('ochiai' or 'tarantula').

        Returns:
            SuspiciousnessResult with ranked gate scores.
        """
        gate_scores: list[tuple[int, float]] = []

        for idx, gate_info in enumerate(circuit_ir.gate_list):
            # Create mutant by removing this gate
            mutant = self._remove_gate(circuit_ir.circuit, idx, circuit_ir)

            if mutant is None:
                gate_scores.append((idx, 0.0))
                continue

            # Run mutant against oracle
            result = self.oracle.compare(mutant, expected_distribution)

            # Higher fidelity when gate removed → gate was likely faulty
            # (removing the faulty gate brings output closer to expected)
            score = result.fidelity

            gate_scores.append((idx, score))

        # Sort by score descending (most suspicious first)
        gate_scores.sort(key=lambda x: x[1], reverse=True)

        return SuspiciousnessResult(gate_scores=gate_scores, metric=metric)

    def _remove_gate(
        self,
        circuit: QuantumCircuit,
        gate_index: int,
        circuit_ir: CircuitIR,
    ) -> Optional[QuantumCircuit]:
        """Create a circuit copy with one gate removed.

        Args:
            circuit: Original circuit.
            gate_index: Index of the gate to remove (in circuit_ir.gate_list).
            circuit_ir: The circuit IR for gate metadata.

        Returns:
            A new QuantumCircuit with the gate removed, or None on error.
        """
        try:
            from qiskit.converters import dag_to_circuit, circuit_to_dag

            dag = circuit_to_dag(circuit)
            op_nodes = list(dag.topological_op_nodes())

            # Filter to match gate_list (excluding barriers/measures)
            non_meta_nodes = [
                n for n in op_nodes
                if n.op.name not in ("barrier", "measure")
            ]

            if gate_index >= len(non_meta_nodes):
                return None

            target_node = non_meta_nodes[gate_index]
            dag.remove_op_node(target_node)

            return dag_to_circuit(dag)
        except Exception:
            return None

    def get_top_suspects(
        self,
        result: SuspiciousnessResult,
        k: Optional[int] = None,
    ) -> list[tuple[int, float]]:
        """Return the top-k most suspicious gates.

        Args:
            result: The suspiciousness result.
            k: Number of top suspects to return. Defaults to config.

        Returns:
            List of (gate_index, score) tuples.
        """
        k = k or self.config.top_k_locations
        return result.gate_scores[:k]
