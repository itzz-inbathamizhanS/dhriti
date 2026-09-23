"""Baseline selectors: random, frequency-based, and exhaustive.

These serve as baselines for comparing the ML and bio-inspired
selectors in experiments.
"""

from __future__ import annotations

import random as rand
from collections import Counter

from dhriti.core.fault import FaultFeatureVector, RepairOperator
from dhriti.selection.selector import RepairSelector


class RandomSelector(RepairSelector):
    """Baseline: selects repair operators uniformly at random."""

    def __init__(self, seed: int = 42):
        self._rng = rand.Random(seed)

    def select(
        self, features: FaultFeatureVector
    ) -> list[tuple[RepairOperator, float]]:
        operators = list(RepairOperator)
        self._rng.shuffle(operators)
        n = len(operators)
        return [(op, 1.0 / n) for op in operators]

    def name(self) -> str:
        return "random"


class FrequencySelector(RepairSelector):
    """Baseline: selects operators by historical frequency.

    Always recommends operators in order of how frequently they
    were the correct repair in the training data.
    """

    def __init__(self):
        self._frequencies: dict[RepairOperator, int] = {
            op: 0 for op in RepairOperator
        }

    def fit(self, labels: list[RepairOperator]) -> None:
        """Compute operator frequencies from training labels."""
        counts = Counter(labels)
        self._frequencies = {op: counts.get(op, 0) for op in RepairOperator}

    def select(
        self, features: FaultFeatureVector
    ) -> list[tuple[RepairOperator, float]]:
        total = max(1, sum(self._frequencies.values()))
        results = [
            (op, count / total)
            for op, count in self._frequencies.items()
        ]
        results.sort(key=lambda x: x[1], reverse=True)
        return results

    def name(self) -> str:
        return "frequency"


class ExhaustiveSelector(RepairSelector):
    """Baseline: tries all operators with equal priority.

    Represents the upper bound on repair coverage but with
    maximum search cost.
    """

    def select(
        self, features: FaultFeatureVector
    ) -> list[tuple[RepairOperator, float]]:
        operators = list(RepairOperator)
        n = len(operators)
        return [(op, 1.0 / n) for op in operators]

    def name(self) -> str:
        return "exhaustive"
