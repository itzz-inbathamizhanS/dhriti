"""Test oracle for fault detection.

Compares the output distribution of a quantum circuit against
an expected reference distribution to detect faults.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
from qiskit.circuit import QuantumCircuit
from qiskit.primitives import StatevectorSampler

from dhriti.core.config import DhritiConfig


@dataclass
class OracleResult:
    """Result of an oracle comparison."""

    is_faulty: bool
    fidelity: float  # 1.0 = perfect match
    kl_divergence: float  # 0.0 = identical distributions
    actual_distribution: dict[str, float]
    expected_distribution: dict[str, float]


class TestOracle:
    """Detects faults by comparing circuit output to expected behavior.

    Uses simulation to obtain output distributions and compares
    against a reference (the correct program's output).
    """

    def __init__(self, config: Optional[DhritiConfig] = None):
        self.config = config or DhritiConfig()
        self.sampler = StatevectorSampler(seed=self.config.numpy_seed)

    def run_circuit(self, circuit: QuantumCircuit) -> dict[str, float]:
        """Execute a circuit and return the normalized output distribution."""
        # Remove all existing measurements and re-add at the end
        # to avoid mid-circuit measurement errors with StatevectorSampler
        meas_circuit = circuit.remove_final_measurements(inplace=False)

        # If remove_final_measurements didn't work (non-final measurements),
        # strip all measurement gates manually
        from qiskit.converters import circuit_to_dag, dag_to_circuit
        dag = circuit_to_dag(meas_circuit)
        measure_nodes = [n for n in dag.topological_op_nodes()
                         if n.op.name == "measure"]
        for node in measure_nodes:
            dag.remove_op_node(node)
        meas_circuit = dag_to_circuit(dag)

        # Remove any classical registers that are now empty
        meas_circuit.measure_all()

        job = self.sampler.run([meas_circuit], shots=self.config.simulator_shots)
        result = job.result()
        counts = result[0].data.meas.get_counts()

        total = sum(counts.values())
        return {k: v / total for k, v in counts.items()}

    def compare(
        self,
        faulty_circuit: QuantumCircuit,
        expected_distribution: dict[str, float],
    ) -> OracleResult:
        """Compare a potentially faulty circuit against expected output.

        Args:
            faulty_circuit: The circuit to test.
            expected_distribution: The reference output distribution
                from the correct program.

        Returns:
            OracleResult with fidelity, KL divergence, and fault status.
        """
        actual = self.run_circuit(faulty_circuit)

        # Compute fidelity (Bhattacharyya coefficient)
        all_keys = set(actual.keys()) | set(expected_distribution.keys())
        fidelity = sum(
            np.sqrt(actual.get(k, 0.0) * expected_distribution.get(k, 0.0))
            for k in all_keys
        )

        # Compute KL divergence (with smoothing)
        epsilon = 1e-10
        kl_div = sum(
            expected_distribution.get(k, epsilon)
            * np.log(
                (expected_distribution.get(k, epsilon) + epsilon)
                / (actual.get(k, epsilon) + epsilon)
            )
            for k in all_keys
        )

        is_faulty = fidelity < self.config.fidelity_threshold

        return OracleResult(
            is_faulty=is_faulty,
            fidelity=float(fidelity),
            kl_divergence=float(max(0.0, kl_div)),
            actual_distribution=actual,
            expected_distribution=expected_distribution,
        )
