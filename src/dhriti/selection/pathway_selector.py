"""Bio-inspired pathway triage selector (for ablation study).

Models DNA repair pathway selection as a decision structure:
different fault characteristics map to different repair "pathways,"
analogous to how different DNA damage types activate different
biological repair mechanisms (BER, NER, HR, NHEJ).

This module exists specifically for the ablation study to test
whether the bio-inspired structure provides algorithmic benefit
over a standard ML classifier.
"""

from __future__ import annotations

from dhriti.core.fault import FaultFeatureVector, RepairOperator
from dhriti.selection.selector import RepairSelector


# Biological pathway mapping:
#
# BER (Base Excision Repair) → small, local damage
#   → GATE_REPLACEMENT (single gate wrong type)
#   → PARAMETER_MODIFICATION (small parameter error)
#
# NER (Nucleotide Excision Repair) → bulky/distorting damage
#   → GATE_DELETION (extra gate causing distortion)
#   → GATE_INSERTION (missing gate)
#
# HR (Homologous Recombination) → structural damage
#   → GATE_ORDER_SWAP (structural reordering)
#   → CONTROL_TARGET_SWAP (connectivity error)
#
# MMR (Mismatch Repair) → replication errors
#   → QUBIT_REASSIGNMENT (wrong qubit)
#   → MEASUREMENT_CORRECTION (wrong measurement)


class PathwaySelector(RepairSelector):
    """Bio-inspired repair pathway triage.

    Maps fault characteristics to repair pathways based on the
    analogy with DNA damage-type-specific repair pathway selection.

    This is a rule-based model, NOT ML-trained. It serves as an
    ablation comparator to test whether the biological structure
    adds value over a standard classifier.
    """

    def select(
        self, features: FaultFeatureVector
    ) -> list[tuple[RepairOperator, float]]:
        """Select repair operators via pathway triage.

        The selection logic follows the biological analogy:
        1. Classify damage type from features
        2. Activate the corresponding pathway
        3. Return operators from that pathway, ranked
        """
        scores: dict[RepairOperator, float] = {op: 0.1 for op in RepairOperator}

        # Pathway 1: BER — small, local damage
        # Indicators: single-qubit gate, has parameters, low local density
        if features.suspect_num_qubits <= 1 and not features.is_entangling:
            if features.has_parameters:
                scores[RepairOperator.PARAMETER_MODIFICATION] += 0.6
                scores[RepairOperator.GATE_REPLACEMENT] += 0.3
            else:
                scores[RepairOperator.GATE_REPLACEMENT] += 0.6
                scores[RepairOperator.PARAMETER_MODIFICATION] += 0.2

        # Pathway 2: NER — bulky/distorting damage
        # Indicators: high local gate density, high output deviation
        if features.local_gate_density > 0.3 or features.output_deviation > 0.5:
            scores[RepairOperator.GATE_DELETION] += 0.5
            scores[RepairOperator.GATE_INSERTION] += 0.4

        # Pathway 3: HR — structural damage
        # Indicators: multi-qubit gate, controlled gate, entangling
        if features.is_entangling or features.is_controlled:
            scores[RepairOperator.CONTROL_TARGET_SWAP] += 0.5
            scores[RepairOperator.GATE_ORDER_SWAP] += 0.4
            scores[RepairOperator.QUBIT_REASSIGNMENT] += 0.3

        # Pathway 4: MMR — mismatch/replication errors
        # Indicators: high suspiciousness but low deviation (subtle error)
        if features.suspiciousness_score > 0.5 and features.output_deviation < 0.3:
            scores[RepairOperator.QUBIT_REASSIGNMENT] += 0.5
            scores[RepairOperator.MEASUREMENT_CORRECTION] += 0.4

        # Normalize and rank
        total = sum(scores.values())
        results = [
            (op, score / total) for op, score in scores.items()
        ]
        results.sort(key=lambda x: x[1], reverse=True)
        return results

    def name(self) -> str:
        return "bio_pathway_triage"
