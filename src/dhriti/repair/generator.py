"""Candidate repair generator.

Combines fault localization, feature extraction, strategy selection,
and repair operator application into a unified pipeline that produces
ranked candidate repairs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from qiskit.circuit import QuantumCircuit

from dhriti.core.circuit_ir import CircuitIR
from dhriti.core.config import DhritiConfig
from dhriti.core.fault import (
    FaultDescriptor,
    FaultFeatureVector,
    RepairCandidate,
    RepairOperator,
)
from dhriti.characterization.features import extract_features
from dhriti.selection.selector import RepairSelector
from dhriti.repair.operators import apply_repair


@dataclass
class GeneratorResult:
    """Result of candidate repair generation."""

    candidates: list[tuple[QuantumCircuit, RepairCandidate]] = field(
        default_factory=list
    )
    total_generated: int = 0
    operators_tried: list[RepairOperator] = field(default_factory=list)


class RepairGenerator:
    """Generates candidate repairs using the selected strategy.

    For each suspicious gate location, extracts features, queries
    the selector for operator recommendations, and applies each
    recommended operator to produce candidate repairs.
    """

    def __init__(
        self,
        selector: RepairSelector,
        config: Optional[DhritiConfig] = None,
    ):
        self.selector = selector
        self.config = config or DhritiConfig()

    def generate(
        self,
        circuit: QuantumCircuit,
        circuit_ir: CircuitIR,
        suspect_gates: list[tuple[int, float]],
        fault: Optional[FaultDescriptor] = None,
    ) -> GeneratorResult:
        """Generate candidate repairs for suspected fault locations.

        Args:
            circuit: The faulty circuit.
            circuit_ir: Parsed circuit IR.
            suspect_gates: List of (gate_index, suspiciousness) from
                the fault localizer, sorted most suspicious first.
            fault: Optional fault descriptor.

        Returns:
            GeneratorResult with all generated candidate repairs.
        """
        import random as rand

        rng = rand.Random(self.config.random_seed)
        result = GeneratorResult()

        # Limit to top-k suspicious locations
        top_suspects = suspect_gates[: self.config.top_k_locations]

        for gate_idx, susp_score in top_suspects:
            # Create fault descriptor for this location
            location_fault = FaultDescriptor(
                suspected_gate_index=gate_idx,
                suspiciousness_score=susp_score,
                output_deviation=fault.output_deviation if fault else 0.0,
            )

            # Extract features
            features = extract_features(circuit_ir, gate_idx, location_fault)

            # Get operator recommendations
            ranked_ops = self.selector.select(features)

            # Apply each recommended operator (up to limit)
            for operator, confidence in ranked_ops[: self.config.max_candidates_per_location]:
                # Sample stochastic operators multiple times
                num_samples = 15 if operator in [
                    RepairOperator.GATE_INSERTION, 
                    RepairOperator.GATE_REPLACEMENT,
                    RepairOperator.PARAMETER_MODIFICATION,
                    RepairOperator.QUBIT_REASSIGNMENT
                ] else 1
                
                for _ in range(num_samples):
                    candidate = RepairCandidate(
                        operator=operator,
                        target_gate_index=gate_idx,
                        confidence=confidence,
                    )

                    repaired = apply_repair(circuit, circuit_ir, candidate, rng)
                    if repaired is not None:
                        result.candidates.append((repaired, candidate))
                        result.operators_tried.append(operator)

                    result.total_generated += 1

                    if len(result.candidates) >= self.config.max_repair_attempts:
                        return result

                if len(result.candidates) >= self.config.max_repair_attempts:
                    return result

        return result
