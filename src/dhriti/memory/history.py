"""Repair history tracking.

Records the outcomes of repair attempts to enable learning
from past repairs. Supports the repair-history feedback
mechanism.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional

from dhriti.core.fault import FaultFeatureVector, RepairOperator, RepairOutcome


@dataclass
class RepairRecord:
    """A single repair attempt record."""

    features: list[float]  # Flattened FaultFeatureVector
    operator: str  # RepairOperator value
    success: bool
    fidelity: float
    timestamp: str = ""


class RepairHistory:
    """Stores and retrieves repair history for feedback.

    Records (features, operator, outcome) tuples to enable:
    1. Training the ML model on accumulated data
    2. Warm-starting repair strategies for recurring faults
    3. Analyzing operator effectiveness by fault type
    """

    def __init__(self):
        self._records: list[RepairRecord] = []

    def record(
        self,
        features: FaultFeatureVector,
        outcome: RepairOutcome,
    ) -> None:
        """Record a repair attempt outcome."""
        self._records.append(
            RepairRecord(
                features=features.to_array(),
                operator=outcome.candidate.operator.value,
                success=outcome.success,
                fidelity=outcome.fidelity,
            )
        )

    def get_training_data(
        self,
    ) -> tuple[list[list[float]], list[str]]:
        """Extract successful repairs as (features, labels) for ML training.

        Returns:
            Tuple of (feature_arrays, operator_labels) from successful repairs.
        """
        features = []
        labels = []
        for r in self._records:
            if r.success:
                features.append(r.features)
                labels.append(r.operator)
        return features, labels

    def operator_success_rates(self) -> dict[str, float]:
        """Compute success rate per operator."""
        from collections import defaultdict

        attempts: dict[str, int] = defaultdict(int)
        successes: dict[str, int] = defaultdict(int)

        for r in self._records:
            attempts[r.operator] += 1
            if r.success:
                successes[r.operator] += 1

        return {
            op: successes[op] / max(1, attempts[op])
            for op in attempts
        }

    def save(self, path: Path) -> None:
        """Save history to JSON."""
        path.parent.mkdir(parents=True, exist_ok=True)
        data = [asdict(r) for r in self._records]
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def load(self, path: Path) -> None:
        """Load history from JSON."""
        with open(path) as f:
            data = json.load(f)
        self._records = [RepairRecord(**d) for d in data]

    @property
    def size(self) -> int:
        return len(self._records)
