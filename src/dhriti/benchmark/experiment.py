"""Experiment runner and metrics for DHRITI evaluation.

Trains selectors, evaluates them, and computes all research metrics:
- Accuracy (top-1 and top-3)
- Search cost (operators tried before success)
- Operator-level precision/recall
- Feature importances
- Ablation comparisons
"""

from __future__ import annotations

import json
import time
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)

from dhriti.core.config import DhritiConfig
from dhriti.core.fault import FaultFeatureVector, RepairOperator
from dhriti.benchmark.dataset import DatasetRecord, DatasetSplit
from dhriti.selection.ml_selector import MLRepairSelector
from dhriti.selection.pathway_selector import PathwaySelector
from dhriti.selection.baselines import (
    RandomSelector,
    FrequencySelector,
    ExhaustiveSelector,
)
from dhriti.selection.selector import RepairSelector


@dataclass
class ExperimentResult:
    """Result of a single experiment run."""

    selector_name: str
    top1_accuracy: float = 0.0
    top3_accuracy: float = 0.0
    avg_rank: float = 0.0  # Average rank of correct operator
    avg_search_cost: float = 0.0  # Avg operators tried before correct
    per_class_report: dict = field(default_factory=dict)
    confusion: list = field(default_factory=list)
    feature_importances: dict = field(default_factory=dict)
    train_time_seconds: float = 0.0
    eval_time_seconds: float = 0.0
    n_train: int = 0
    n_test: int = 0


def _records_to_features_labels(
    records: list[DatasetRecord],
) -> tuple[list[FaultFeatureVector], list[RepairOperator]]:
    """Convert dataset records to features and labels."""
    features = []
    labels = []
    for r in records:
        fv = FaultFeatureVector()
        arr = r.features
        if len(arr) == 24:
            fv.num_qubits = int(arr[0])
            fv.circuit_depth = int(arr[1])
            fv.total_gate_count = int(arr[2])
            fv.parameter_count = int(arr[3])
            fv.measurement_count = int(arr[4])
            fv.cx_count = int(arr[5])
            fv.h_count = int(arr[6])
            fv.x_count = int(arr[7])
            fv.rz_count = int(arr[8])
            fv.ry_count = int(arr[9])
            fv.rx_count = int(arr[10])
            fv.t_count = int(arr[11])
            fv.s_count = int(arr[12])
            fv.other_gate_count = int(arr[13])
            fv.suspect_gate_type_encoded = int(arr[14])
            fv.suspect_gate_position = int(arr[15])
            fv.suspect_gate_depth = int(arr[16])
            fv.suspect_num_qubits = int(arr[17])
            fv.local_gate_density = float(arr[18])
            fv.has_parameters = bool(arr[19])
            fv.is_controlled = bool(arr[20])
            fv.is_entangling = bool(arr[21])
            fv.suspiciousness_score = float(arr[22])
            fv.output_deviation = float(arr[23])
        features.append(fv)
        labels.append(RepairOperator(r.ground_truth_repair))
    return features, labels


def evaluate_selector(
    selector: RepairSelector,
    test_features: list[FaultFeatureVector],
    test_labels: list[RepairOperator],
) -> ExperimentResult:
    """Evaluate a selector on test data.

    Computes top-1 accuracy, top-3 accuracy, average rank of
    correct operator, and average search cost.
    """
    start = time.time()

    correct_top1 = 0
    correct_top3 = 0
    total_rank = 0
    total_cost = 0

    y_true = []
    y_pred = []

    for features, true_label in zip(test_features, test_labels):
        ranked = selector.select(features)
        predicted_ops = [op for op, _ in ranked]

        # Top-1
        if predicted_ops and predicted_ops[0] == true_label:
            correct_top1 += 1

        # Top-3
        if true_label in predicted_ops[:3]:
            correct_top3 += 1

        # Rank of correct operator
        if true_label in predicted_ops:
            rank = predicted_ops.index(true_label) + 1
        else:
            rank = len(RepairOperator)
        total_rank += rank

        # Search cost = rank (operators tried before finding correct)
        total_cost += rank

        y_true.append(true_label.value)
        y_pred.append(predicted_ops[0].value if predicted_ops else "unknown")

    n = len(test_labels)
    eval_time = time.time() - start

    # Classification report
    try:
        report = classification_report(y_true, y_pred, output_dict=True, zero_division=0)
    except Exception:
        report = {}

    # Confusion matrix
    try:
        cm = confusion_matrix(y_true, y_pred).tolist()
    except Exception:
        cm = []

    # Feature importances (if available)
    importances = {}
    if hasattr(selector, "feature_importances"):
        try:
            importances = selector.feature_importances()
        except Exception:
            pass

    return ExperimentResult(
        selector_name=selector.name(),
        top1_accuracy=correct_top1 / max(1, n),
        top3_accuracy=correct_top3 / max(1, n),
        avg_rank=total_rank / max(1, n),
        avg_search_cost=total_cost / max(1, n),
        per_class_report=report,
        confusion=cm,
        feature_importances=importances,
        eval_time_seconds=eval_time,
        n_test=n,
    )


def run_all_experiments(
    split: DatasetSplit,
    config: Optional[DhritiConfig] = None,
    verbose: bool = True,
) -> list[ExperimentResult]:
    """Run all experiments: train ML selector, evaluate all selectors.

    Experiments:
    1. Random baseline
    2. Frequency baseline
    3. Exhaustive baseline
    4. Bio-inspired pathway selector
    5. ML Random Forest selector (CORE CONTRIBUTION)

    Returns:
        List of ExperimentResult for each selector.
    """
    config = config or DhritiConfig()
    config.seed_all()

    # Convert data
    train_features, train_labels = _records_to_features_labels(split.train)
    val_features, val_labels = _records_to_features_labels(split.val)
    test_features, test_labels = _records_to_features_labels(split.test)

    if verbose:
        print(f"Train: {len(train_features)}, Val: {len(val_features)}, "
              f"Test: {len(test_features)}")

    results: list[ExperimentResult] = []

    # 1. Random baseline
    if verbose:
        print("\n[1/5] Random baseline...")
    random_sel = RandomSelector(seed=config.random_seed)
    r = evaluate_selector(random_sel, test_features, test_labels)
    r.n_train = 0
    results.append(r)
    if verbose:
        print(f"  Top-1: {r.top1_accuracy:.3f}, Top-3: {r.top3_accuracy:.3f}, "
              f"Avg rank: {r.avg_rank:.2f}")

    # 2. Frequency baseline
    if verbose:
        print("\n[2/5] Frequency baseline...")
    freq_sel = FrequencySelector()
    freq_sel.fit(train_labels)
    r = evaluate_selector(freq_sel, test_features, test_labels)
    r.n_train = len(train_labels)
    results.append(r)
    if verbose:
        print(f"  Top-1: {r.top1_accuracy:.3f}, Top-3: {r.top3_accuracy:.3f}, "
              f"Avg rank: {r.avg_rank:.2f}")

    # 3. Exhaustive baseline
    if verbose:
        print("\n[3/5] Exhaustive baseline...")
    exh_sel = ExhaustiveSelector()
    r = evaluate_selector(exh_sel, test_features, test_labels)
    r.n_train = 0
    results.append(r)
    if verbose:
        print(f"  Top-1: {r.top1_accuracy:.3f}, Top-3: {r.top3_accuracy:.3f}, "
              f"Avg rank: {r.avg_rank:.2f}")

    # 4. Bio-inspired pathway selector
    if verbose:
        print("\n[4/5] Bio-inspired pathway selector...")
    pathway_sel = PathwaySelector()
    r = evaluate_selector(pathway_sel, test_features, test_labels)
    r.n_train = 0
    results.append(r)
    if verbose:
        print(f"  Top-1: {r.top1_accuracy:.3f}, Top-3: {r.top3_accuracy:.3f}, "
              f"Avg rank: {r.avg_rank:.2f}")

    # 5. ML Random Forest selector (CORE CONTRIBUTION)
    if verbose:
        print("\n[5/5] ML Random Forest selector (CORE)...")
    ml_sel = MLRepairSelector(
        n_estimators=config.ml_n_estimators,
        max_depth=config.ml_max_depth,
        random_state=config.random_seed,
    )
    t0 = time.time()
    train_metrics = ml_sel.train(train_features, train_labels)
    train_time = time.time() - t0

    if verbose:
        print(f"  Training: {train_metrics}")

    # Evaluate on validation set first
    val_result = evaluate_selector(ml_sel, val_features, val_labels)
    if verbose:
        print(f"  Val Top-1: {val_result.top1_accuracy:.3f}, "
              f"Val Top-3: {val_result.top3_accuracy:.3f}")

    # Evaluate on test set
    r = evaluate_selector(ml_sel, test_features, test_labels)
    r.train_time_seconds = train_time
    r.n_train = len(train_labels)
    results.append(r)
    if verbose:
        print(f"  Test Top-1: {r.top1_accuracy:.3f}, Top-3: {r.top3_accuracy:.3f}, "
              f"Avg rank: {r.avg_rank:.2f}")

        # Feature importances
        if r.feature_importances:
            sorted_imp = sorted(
                r.feature_importances.items(),
                key=lambda x: x[1],
                reverse=True,
            )
            print(f"  Top-5 features: {sorted_imp[:5]}")

    return results


def print_comparison_table(results: list[ExperimentResult]) -> None:
    """Print a formatted comparison table of all selectors."""
    print("\n" + "=" * 80)
    print(f"{'Selector':<25} {'Top-1':>7} {'Top-3':>7} {'Avg Rank':>9} "
          f"{'Search Cost':>12} {'Train(s)':>9}")
    print("-" * 80)
    for r in results:
        print(f"{r.selector_name:<25} {r.top1_accuracy:>7.3f} "
              f"{r.top3_accuracy:>7.3f} {r.avg_rank:>9.2f} "
              f"{r.avg_search_cost:>12.2f} {r.train_time_seconds:>9.2f}")
    print("=" * 80)


def save_results(results: list[ExperimentResult], path: Path) -> None:
    """Save experiment results to JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    data = [asdict(r) for r in results]
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)
