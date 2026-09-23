"""Main experiment: generate dataset, train ML selector, evaluate all selectors.

This is the primary experiment script for DHRITI. It:
1. Generates a synthetic benchmark dataset
2. Splits into train/val/test
3. Trains the ML selector
4. Evaluates all 5 selectors
5. Reports results
"""

import sys
import time
from pathlib import Path

from dhriti.core.config import DhritiConfig
from dhriti.benchmark.dataset import (
    generate_dataset,
    split_dataset,
    save_dataset,
)
from dhriti.benchmark.experiment import (
    run_all_experiments,
    print_comparison_table,
    save_results,
)


def main():
    print("=" * 60)
    print("DHRITI - Main Experiment")
    print("=" * 60)

    config = DhritiConfig(
        random_seed=42,
        numpy_seed=42,
        simulator_shots=2048,  # Reduced for speed
        ml_n_estimators=100,
        ml_max_depth=None,
    )
    config.seed_all()

    output_dir = Path("experiments")
    output_dir.mkdir(exist_ok=True)

    # Phase 1: Generate dataset
    print("\n[PHASE 1] Generating synthetic benchmark dataset...")
    print("  Circuits: 6 families x (3-10 qubits) x 2 variants")
    print("  Mutations: 5 per circuit")

    t0 = time.time()
    records = generate_dataset(
        config=config,
        min_qubits=3,
        max_qubits=10,  # 3-10 qubits for speed
        circuits_per_config=2,
        mutations_per_circuit=5,
        verbose=True,
    )
    gen_time = time.time() - t0
    print(f"  Generation time: {gen_time:.1f}s")

    if len(records) < 10:
        print("ERROR: Not enough records generated. Aborting.")
        sys.exit(1)

    # Save dataset
    save_dataset(records, output_dir / "dataset.json")
    print(f"  Saved {len(records)} records to {output_dir / 'dataset.json'}")

    # Phase 2: Split dataset
    print("\n[PHASE 2] Splitting dataset (70/15/15)...")
    split = split_dataset(records, train_ratio=0.7, val_ratio=0.15, seed=42)
    print(f"  Train: {len(split.train)}, Val: {len(split.val)}, "
          f"Test: {len(split.test)}")

    # Phase 3: Run experiments
    print("\n[PHASE 3] Running experiments...")
    results = run_all_experiments(split, config=config, verbose=True)

    # Phase 4: Print comparison
    print_comparison_table(results)

    # Save results
    save_results(results, output_dir / "results.json")
    print(f"\nResults saved to {output_dir / 'results.json'}")

    # Summary
    ml_result = [r for r in results if r.selector_name == "ml_random_forest"][0]
    random_result = [r for r in results if r.selector_name == "random"][0]
    pathway_result = [r for r in results if r.selector_name == "bio_pathway_triage"][0]

    print("\n" + "=" * 60)
    print("KEY FINDINGS")
    print("=" * 60)
    print(f"ML selector top-1 accuracy:       {ml_result.top1_accuracy:.3f}")
    print(f"Random baseline top-1 accuracy:    {random_result.top1_accuracy:.3f}")
    print(f"Pathway selector top-1 accuracy:   {pathway_result.top1_accuracy:.3f}")
    print(f"ML improvement over random:        "
          f"{(ml_result.top1_accuracy - random_result.top1_accuracy):.3f}")
    print(f"ML improvement over pathway:       "
          f"{(ml_result.top1_accuracy - pathway_result.top1_accuracy):.3f}")
    print(f"ML search cost reduction:          "
          f"{(1 - ml_result.avg_search_cost / max(0.01, random_result.avg_search_cost)):.1%}")

    if ml_result.feature_importances:
        sorted_imp = sorted(
            ml_result.feature_importances.items(),
            key=lambda x: x[1],
            reverse=True,
        )
        print(f"\nTop-5 most important features:")
        for name, imp in sorted_imp[:5]:
            print(f"  {name}: {imp:.4f}")


if __name__ == "__main__":
    main()
