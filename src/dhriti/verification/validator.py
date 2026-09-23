"""Semantic validation of candidate repairs.

Verifies that a repaired circuit produces output that matches
the expected behavior of the original correct program.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from qiskit.circuit import QuantumCircuit

from dhriti.core.config import DhritiConfig
from dhriti.core.fault import RepairCandidate, RepairOutcome
from dhriti.detection.oracle import TestOracle


class RepairValidator:
    """Validates candidate repairs against expected behavior.

    Uses the test oracle to verify functional correctness and
    ranks candidates by fidelity.
    """

    def __init__(self, config: Optional[DhritiConfig] = None):
        self.config = config or DhritiConfig()
        self.oracle = TestOracle(config=self.config)

    def validate(
        self,
        candidate_circuit: QuantumCircuit,
        candidate: RepairCandidate,
        expected_distribution: dict[str, float],
    ) -> RepairOutcome:
        """Validate a single candidate repair.

        Args:
            candidate_circuit: The repaired circuit to validate.
            candidate: The repair candidate descriptor.
            expected_distribution: Expected output from correct program.

        Returns:
            RepairOutcome with validation results.
        """
        try:
            # Check compilation (Qiskit will raise on invalid circuits)
            _ = candidate_circuit.depth()
            compilation_success = True
        except Exception:
            return RepairOutcome(
                candidate=candidate,
                success=False,
                compilation_success=False,
            )

        try:
            result = self.oracle.compare(candidate_circuit, expected_distribution)
            execution_success = True
        except Exception:
            return RepairOutcome(
                candidate=candidate,
                success=False,
                compilation_success=True,
                execution_success=False,
            )

        passes = result.fidelity >= self.config.fidelity_threshold

        return RepairOutcome(
            candidate=candidate,
            success=passes,
            fidelity=result.fidelity,
            distribution_similarity=1.0 - result.kl_divergence,
            compilation_success=compilation_success,
            execution_success=execution_success,
            passes_tests=passes,
        )

    def validate_and_rank(
        self,
        candidates: list[tuple[QuantumCircuit, RepairCandidate]],
        expected_distribution: dict[str, float],
    ) -> list[RepairOutcome]:
        """Validate all candidates and rank by fidelity.

        Args:
            candidates: List of (circuit, candidate) tuples.
            expected_distribution: Expected output.

        Returns:
            List of RepairOutcome sorted by fidelity descending.
        """
        outcomes = []
        for circuit, candidate in candidates:
            outcome = self.validate(circuit, candidate, expected_distribution)
            outcomes.append(outcome)

        # Sort by fidelity descending (best repairs first)
        outcomes.sort(key=lambda o: o.fidelity, reverse=True)
        return outcomes
