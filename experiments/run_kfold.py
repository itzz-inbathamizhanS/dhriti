"""Full-scale experiment with k-fold cross-validation.

Generates a larger dataset (3-15 qubits) and runs stratified
k-fold cross-validation for statistical robustness.
"""

import json
import time
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from sklearn.model_selection import StratifiedKFold

from dhriti.core.config import DhritiConfig
from dhriti.core.fault import FaultFeatureVector, RepairOperator
from dhriti.benchmark.dataset import generate_dataset, save_dataset
from dhriti.benchmark.experiment import (
    _records_to_features_labels,
    evaluate_selector,
    ExperimentResult,
)
from dhriti.selection.ml_selector import MLRepairSelector
from dhriti.selection.pathway_selector import PathwaySelector
from dhriti.selection.baselines import RandomSelector, FrequencySelector


def run_kfold_experiment(k: int = 5):
    print("=" * 60)
    print(f"DHRITI - Full-Scale {k}-Fold Cross-Validation Experiment")
    print("=" * 60)

    config = DhritiConfig(
        random_seed=42,
        numpy_seed=42,
        simulator_shots=2048,
        ml_n_estimators=200,
    )
    config.seed_all()

    output_dir = Path("experiments")
    output_dir.mkdir(exist_ok=True)

    # Generate larger dataset
    print("\n[1] Generating full-scale dataset (3-15 qubits)...")
    t0 = time.time()
    records = generate_dataset(
        config=config,
        min_qubits=3,
        max_qubits=15,
        circuits_per_config=3,
        mutations_per_circuit=7,
        verbose=True,
    )
    gen_time = time.time() - t0
    print(f"  Time: {gen_time:.1f}s, Records: {len(records)}")

    if len(records) < 50:
        print("ERROR: Too few records. Aborting.")
        sys.exit(1)

    save_dataset(records, output_dir / "dataset_full.json")

    # Prepare data
    features, labels = _records_to_features_labels(records)
    X = np.array([f.to_array() for f in features])
    y = np.array([op.value for op in labels])

    # K-fold cross-validation
    print(f"\n[2] Running {k}-fold stratified cross-validation...")
    skf = StratifiedKFold(n_splits=k, shuffle=True, random_state=42)

    selector_names = ["random", "frequency", "bio_pathway_triage", "ml_random_forest"]
    fold_results: dict[str, list[dict]] = {name: [] for name in selector_names}

    for fold_idx, (train_idx, test_idx) in enumerate(skf.split(X, y)):
        print(f"\n  --- Fold {fold_idx + 1}/{k} (train={len(train_idx)}, test={len(test_idx)}) ---")

        train_features = [features[i] for i in train_idx]
        train_labels = [labels[i] for i in train_idx]
        test_features = [features[i] for i in test_idx]
        test_labels = [labels[i] for i in test_idx]

        # Random
        sel = RandomSelector(seed=42 + fold_idx)
        r = evaluate_selector(sel, test_features, test_labels)
        fold_results["random"].append({"top1": r.top1_accuracy, "top3": r.top3_accuracy,
                                       "rank": r.avg_rank, "cost": r.avg_search_cost})

        # Frequency
        sel = FrequencySelector()
        sel.fit(train_labels)
        r = evaluate_selector(sel, test_features, test_labels)
        fold_results["frequency"].append({"top1": r.top1_accuracy, "top3": r.top3_accuracy,
                                          "rank": r.avg_rank, "cost": r.avg_search_cost})

        # Pathway
        sel = PathwaySelector()
        r = evaluate_selector(sel, test_features, test_labels)
        fold_results["bio_pathway_triage"].append({"top1": r.top1_accuracy, "top3": r.top3_accuracy,
                                                   "rank": r.avg_rank, "cost": r.avg_search_cost})

        # ML
        sel = MLRepairSelector(n_estimators=200, random_state=42)
        sel.train(train_features, train_labels)
        r = evaluate_selector(sel, test_features, test_labels)
        fold_results["ml_random_forest"].append({"top1": r.top1_accuracy, "top3": r.top3_accuracy,
                                                 "rank": r.avg_rank, "cost": r.avg_search_cost})

        print(f"    ML top-1: {r.top1_accuracy:.3f}, top-3: {r.top3_accuracy:.3f}")

    # Aggregate results
    print("\n" + "=" * 90)
    print(f"{'Selector':<25} {'Top-1 (mean+/-std)':>20} {'Top-3 (mean+/-std)':>20} "
          f"{'Avg Rank':>15} {'Cost':>10}")
    print("-" * 90)

    summary = {}
    for name in selector_names:
        folds = fold_results[name]
        t1 = [f["top1"] for f in folds]
        t3 = [f["top3"] for f in folds]
        ranks = [f["rank"] for f in folds]
        costs = [f["cost"] for f in folds]
        summary[name] = {
            "top1_mean": float(np.mean(t1)), "top1_std": float(np.std(t1)),
            "top3_mean": float(np.mean(t3)), "top3_std": float(np.std(t3)),
            "rank_mean": float(np.mean(ranks)), "rank_std": float(np.std(ranks)),
            "cost_mean": float(np.mean(costs)), "cost_std": float(np.std(costs)),
        }
        print(f"{name:<25} {np.mean(t1):>7.3f} +/- {np.std(t1):.3f}   "
              f"{np.mean(t3):>7.3f} +/- {np.std(t3):.3f}   "
              f"{np.mean(ranks):>7.2f} +/- {np.std(ranks):.2f}   "
              f"{np.mean(costs):>7.2f}")
    print("=" * 90)

    # Final ML model on all data for feature importances
    print("\n[3] Training final model on all data for feature importances...")
    final_ml = MLRepairSelector(n_estimators=200, random_state=42)
    train_metrics = final_ml.train(features, labels)
    importances = final_ml.feature_importances()
    sorted_imp = sorted(importances.items(), key=lambda x: x[1], reverse=True)

    print(f"\nFeature importances (all {len(sorted_imp)} features):")
    for name, imp in sorted_imp:
        bar = "#" * int(imp * 100)
        print(f"  {name:<30} {imp:.4f} {bar}")

    # Save model
    final_ml.save(output_dir / "ml_model.joblib")
    print(f"\nModel saved to {output_dir / 'ml_model.joblib'}")

    # Save results
    results_data = {
        "k_folds": k,
        "n_records": len(records),
        "fold_results": fold_results,
        "summary": summary,
        "feature_importances": importances,
        "train_metrics": train_metrics,
    }
    with open(output_dir / "results_kfold.json", "w") as f:
        json.dump(results_data, f, indent=2, default=str)

    # Key findings
    ml_s = summary["ml_random_forest"]
    rand_s = summary["random"]
    pw_s = summary["bio_pathway_triage"]

    print("\n" + "=" * 60)
    print("KEY FINDINGS")
    print("=" * 60)
    print(f"ML top-1 accuracy:    {ml_s['top1_mean']:.3f} +/- {ml_s['top1_std']:.3f}")
    print(f"Random top-1:         {rand_s['top1_mean']:.3f} +/- {rand_s['top1_std']:.3f}")
    print(f"Pathway top-1:        {pw_s['top1_mean']:.3f} +/- {pw_s['top1_std']:.3f}")
    print(f"ML improvement:       +{ml_s['top1_mean'] - rand_s['top1_mean']:.3f} over random")
    print(f"Search cost reduction: "
          f"{(1 - ml_s['cost_mean'] / max(0.01, rand_s['cost_mean'])):.1%}")


if __name__ == "__main__":
    run_kfold_experiment(k=5)
