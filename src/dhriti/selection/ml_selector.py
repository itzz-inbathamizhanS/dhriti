"""ML-based repair operator selector (CORE CONTRIBUTION).

Uses a Random Forest classifier trained on FaultFeatureVectors
to predict which RepairOperator is most likely to produce a
successful repair. This is the primary research contribution
of DHṚTI.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

from dhriti.core.fault import FaultFeatureVector, RepairOperator
from dhriti.selection.selector import RepairSelector


class MLRepairSelector(RepairSelector):
    """Random Forest-based repair operator selector.

    Trained on (FaultFeatureVector, RepairOperator) pairs from
    the benchmark dataset. Predicts the most appropriate repair
    operator given fault characteristics.
    """

    def __init__(
        self,
        n_estimators: int = 100,
        max_depth: Optional[int] = None,
        random_state: int = 42,
    ):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.random_state = random_state

        self._model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state,
            n_jobs=-1,
        )
        self._label_encoder = LabelEncoder()
        self._is_trained = False
        self._operators = list(RepairOperator)

    def train(
        self,
        features: list[FaultFeatureVector],
        labels: list[RepairOperator],
    ) -> dict[str, float]:
        """Train the Random Forest on labeled repair data.

        Args:
            features: List of fault feature vectors.
            labels: Corresponding ground-truth repair operators.

        Returns:
            Dict with training metrics (accuracy, etc.).
        """
        X = np.array([f.to_array() for f in features])
        y_str = [op.value for op in labels]
        y = self._label_encoder.fit_transform(y_str)

        self._model.fit(X, y)
        self._is_trained = True

        # Training accuracy (for diagnostic; NOT evaluation)
        train_acc = self._model.score(X, y)

        return {
            "train_accuracy": train_acc,
            "n_samples": len(features),
            "n_features": X.shape[1],
            "n_classes": len(self._label_encoder.classes_),
        }

    def select(
        self, features: FaultFeatureVector
    ) -> list[tuple[RepairOperator, float]]:
        """Predict repair operators ranked by confidence.

        Args:
            features: The extracted fault feature vector.

        Returns:
            Ranked list of (operator, probability) tuples.

        Raises:
            RuntimeError: If the model has not been trained.
        """
        if not self._is_trained:
            raise RuntimeError("MLRepairSelector has not been trained. Call train() first.")

        X = np.array([features.to_array()])
        probabilities = self._model.predict_proba(X)[0]

        # Map back to RepairOperator enum
        results: list[tuple[RepairOperator, float]] = []
        for idx, prob in enumerate(probabilities):
            label_str = self._label_encoder.inverse_transform([idx])[0]
            operator = RepairOperator(label_str)
            results.append((operator, float(prob)))

        # Sort by probability descending
        results.sort(key=lambda x: x[1], reverse=True)
        return results

    def feature_importances(self) -> dict[str, float]:
        """Return feature importance scores from the trained model.

        Useful for interpretability and understanding which circuit
        features most influence operator selection.
        """
        if not self._is_trained:
            raise RuntimeError("Model not trained.")

        names = FaultFeatureVector.feature_names()
        importances = self._model.feature_importances_
        return dict(zip(names, importances))

    def name(self) -> str:
        return "ml_random_forest"

    def save(self, path: Path) -> None:
        """Save the trained model to disk."""
        import joblib
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(
            {"model": self._model, "encoder": self._label_encoder},
            path,
        )

    def load(self, path: Path) -> None:
        """Load a trained model from disk."""
        import joblib
        data = joblib.load(path)
        self._model = data["model"]
        self._label_encoder = data["encoder"]
        self._is_trained = True
