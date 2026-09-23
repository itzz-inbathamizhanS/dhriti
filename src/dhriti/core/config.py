"""Configuration and reproducibility utilities for DHṚTI."""

from __future__ import annotations

import json
import random
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import numpy as np


@dataclass
class DhritiConfig:
    """Global configuration for a DHṚTI run.

    Records all settings needed for reproducibility.
    """

    # Reproducibility
    random_seed: int = 42
    numpy_seed: int = 42

    # Simulation
    simulator_shots: int = 8192
    fidelity_threshold: float = 0.95

    # Repair search
    max_candidates_per_location: int = 10
    max_repair_attempts: int = 100
    top_k_locations: int = 5

    # ML model
    ml_model_type: str = "random_forest"
    ml_n_estimators: int = 100
    ml_max_depth: Optional[int] = None

    # Circuit scale
    min_qubits: int = 3
    max_qubits: int = 15

    # Paths
    dataset_dir: str = "datasets"
    experiment_dir: str = "experiments"

    # Metadata
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def seed_all(self) -> None:
        """Set all random seeds for reproducibility."""
        random.seed(self.random_seed)
        np.random.seed(self.numpy_seed)

    def save(self, path: Path) -> None:
        """Save configuration to JSON."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(asdict(self), f, indent=2)

    @classmethod
    def load(cls, path: Path) -> DhritiConfig:
        """Load configuration from JSON."""
        with open(path) as f:
            data = json.load(f)
        return cls(**data)
