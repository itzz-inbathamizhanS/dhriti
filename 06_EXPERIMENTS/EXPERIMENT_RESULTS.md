# DHRITI Experimental Results

## Full-Scale 5-Fold Cross-Validation

### Dataset

- **234 correct circuits** across 6 families (bell/GHZ, superposition, entangled chain, rotation, QFT-like, random deep)
- **3-15 qubits**, 3 variants per family per qubit count
- **1,131 mutated records** across 6 fault types
- **39 errors** during generation (circuits where mutation was not applicable)
- Generation time: 42.4 seconds

### Fault Distribution

| Fault Type | Count |
|-----------|------:|
| missing_gate | 234 |
| extra_gate | 234 |
| wrong_gate | 234 |
| wrong_qubit | 234 |
| wrong_control | 156 |
| wrong_parameter | 39 |

### Results (5-Fold Stratified Cross-Validation)

| Selector | Top-1 (mean +/- std) | Top-3 (mean +/- std) | Avg Rank | Search Cost |
|----------|---------------------:|---------------------:|---------:|------------:|
| random | 0.117 +/- 0.010 | 0.350 +/- 0.020 | 4.58 | 4.58 |
| frequency | 0.204 +/- 0.001 | 0.620 +/- 0.001 | 2.97 | 2.97 |
| bio_pathway_triage | 0.174 +/- 0.024 | 0.422 +/- 0.033 | 4.01 | 4.01 |
| **ml_random_forest** | **0.599 +/- 0.040** | **0.892 +/- 0.034** | **1.78** | **1.78** |

### Per-Fold ML Results

| Fold | Top-1 | Top-3 |
|:----:|------:|------:|
| 1 | 0.670 | 0.925 |
| 2 | 0.597 | 0.938 |
| 3 | 0.575 | 0.876 |
| 4 | 0.549 | 0.872 |
| 5 | 0.602 | 0.850 |

### Key Findings

| Metric | Value |
|--------|------:|
| ML top-1 accuracy | 59.9% +/- 4.0% |
| ML top-3 accuracy | 89.2% +/- 3.4% |
| Random baseline top-1 | 11.7% +/- 1.0% |
| Pathway selector top-1 | 17.4% +/- 2.4% |
| ML improvement over random | +48.2 pp |
| ML improvement over pathway | +42.5 pp |
| Search cost reduction vs random | 61.1% |
| ML average rank | 1.78 / 6 operators |

### Feature Importances (All 24 Features)

| Rank | Feature | Importance |
|:----:|---------|----------:|
| 1 | suspect_gate_position | 0.1062 |
| 2 | output_deviation | 0.1014 |
| 3 | circuit_depth | 0.0959 |
| 4 | local_gate_density | 0.0827 |
| 5 | suspect_gate_depth | 0.0782 |
| 6 | other_gate_count | 0.0730 |
| 7 | total_gate_count | 0.0631 |
| 8 | suspect_gate_type_encoded | 0.0582 |
| 9 | cx_count | 0.0502 |
| 10 | num_qubits | 0.0449 |
| 11 | h_count | 0.0428 |
| 12 | s_count | 0.0345 |
| 13 | t_count | 0.0323 |
| 14 | x_count | 0.0302 |
| 15 | parameter_count | 0.0249 |
| 16 | ry_count | 0.0136 |
| 17 | rz_count | 0.0135 |
| 18 | rx_count | 0.0128 |
| 19 | is_controlled | 0.0122 |
| 20 | has_parameters | 0.0106 |
| 21 | suspect_num_qubits | 0.0100 |
| 22 | is_entangling | 0.0088 |
| 23 | measurement_count | 0.0000 |
| 24 | suspiciousness_score | 0.0000 |

### Observations

1. **ML dominates all baselines**: The Random Forest selector achieves ~60% top-1 accuracy, 5.1x better than random (11.7%) and 3.4x better than the bio-pathway triage (17.4%).

2. **Top-3 accuracy is very high**: At 89.2%, the correct operator is almost always in the top 3 ML predictions, meaning the ML selector substantially reduces the search space.

3. **Feature importance is distributed**: No single feature dominates. The top 5 features (gate position, output deviation, circuit depth, local density, gate depth) collectively account for ~46% of importance, all of which are circuit-structural features. This confirms the hypothesis that circuit structure is informative for operator selection.

4. **Bio-pathway provides marginal improvement**: The pathway selector (17.4%) slightly outperforms random (11.7%) but substantially underperforms ML. This suggests the biological pathway structure captures some useful heuristics but cannot match a data-driven learned model.

5. **Measurement_count and suspiciousness_score have zero importance**: These features provide no signal in the current dataset. The suspiciousness_score was set to a constant 0.9 in the synthetic data (since we know the fault location), which explains its zero importance; in a real scenario with spectrum-based FL, this would carry more weight.

6. **Standard deviation is low**: The +/- 4.0% std for ML top-1 across 5 folds indicates stable, reliable performance.

### Limitations

- Synthetic dataset only (no real-world Bugs4Q evaluation yet)
- Ground-truth fault location is known (suspiciousness_score is constant)
- Unbalanced fault type distribution (wrong_parameter has only 39 samples)
- No comparison with QRep or LLM-based baselines (would require their implementations)
- Single ML model (Random Forest); GNN alternative not yet tested
