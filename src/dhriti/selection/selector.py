"""Abstract repair selector interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from dhriti.core.fault import FaultFeatureVector, RepairOperator


class RepairSelector(ABC):
    """Abstract base class for repair strategy selectors.

    All selectors take a FaultFeatureVector and return a ranked
    list of (RepairOperator, confidence) tuples, ordered from
    most to least recommended.
    """

    @abstractmethod
    def select(
        self, features: FaultFeatureVector
    ) -> list[tuple[RepairOperator, float]]:
        """Select and rank repair operators for a fault.

        Args:
            features: The extracted fault feature vector.

        Returns:
            Ranked list of (operator, confidence) tuples.
            Confidence values should be in [0, 1].
        """
        ...

    @abstractmethod
    def name(self) -> str:
        """Return the name of this selector for logging."""
        ...
