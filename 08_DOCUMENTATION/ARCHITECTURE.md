# DHṚTI Architecture

## Finalized Research Direction

**Primary Contribution**: A dedicated, interpretable ML model (Random Forest) trained on circuit-structural and fault-characterization features that selects which repair operator to apply for faulty quantum programs.

**Positioning**: Lightweight, interpretable, non-LLM alternative to LLM-based quantum repair.

**Biological Inspiration**: Structural metaphor for repair-pathway triage (tested via ablation).

---

## Module Structure

```
src/dhriti/
├── __init__.py              # Package metadata
├── cli.py                   # CLI entry points
│
├── core/                    # Core data structures
│   ├── __init__.py
│   ├── circuit_ir.py        # Circuit intermediate representation (DAG wrapper)
│   ├── fault.py             # Fault descriptor (type, location, features)
│   ├── repair.py            # Repair descriptor (operator, location, parameters)
│   └── config.py            # Configuration and reproducibility
│
├── parser/                  # Quantum program parser
│   ├── __init__.py
│   └── qiskit_parser.py     # Qiskit QuantumCircuit → CircuitIR
│
├── detection/               # Fault detection
│   ├── __init__.py
│   └── oracle.py            # Test oracle: expected vs actual distribution
│
├── localization/            # Fault localization
│   ├── __init__.py
│   └── spectrum.py          # Spectrum-based fault localization (Ochiai, Tarantula)
│
├── characterization/        # Fault characterization (feature extraction)
│   ├── __init__.py
│   └── features.py          # Circuit-structural + fault feature extraction
│
├── selection/               # Repair strategy selection (CORE CONTRIBUTION)
│   ├── __init__.py
│   ├── selector.py          # Abstract selector interface
│   ├── ml_selector.py       # Random Forest operator selector
│   ├── pathway_selector.py  # Bio-inspired pathway triage (for ablation)
│   ├── random_selector.py   # Random baseline
│   ├── frequency_selector.py # Frequency-based baseline
│   └── exhaustive_selector.py # Exhaustive search baseline
│
├── repair/                  # Repair generation
│   ├── __init__.py
│   ├── operators.py         # Repair operator implementations
│   └── generator.py         # Candidate repair generator
│
├── verification/            # Repair verification
│   ├── __init__.py
│   └── validator.py         # Semantic validation (fidelity, distribution similarity)
│
├── memory/                  # Repair history
│   ├── __init__.py
│   └── history.py           # Repair outcome tracking
│
└── benchmark/               # Dataset and experiment infrastructure
    ├── __init__.py
    ├── mutation.py           # Mutation operator framework
    ├── dataset.py            # Dataset generation and management
    └── experiment.py         # Experiment runner and metrics
```

---

## Data Flow

```
Input: Faulty QuantumCircuit + Test Oracle (expected behavior)
                    │
                    ▼
            ┌──────────────┐
            │  parser/      │  Qiskit QuantumCircuit → CircuitIR (DAG)
            └──────┬───────┘
                    │ CircuitIR
                    ▼
            ┌──────────────┐
            │  detection/   │  Run circuit, compare with oracle
            └──────┬───────┘
                    │ FaultDetected (bool) + execution results
                    ▼
            ┌──────────────┐
            │  localization/│  Spectrum-based suspiciousness scoring
            └──────┬───────┘
                    │ Ranked suspicious gate locations
                    ▼
            ┌──────────────┐
            │ characterize/ │  Extract circuit-structural + fault features
            └──────┬───────┘
                    │ FaultFeatureVector
                    ▼
            ┌──────────────┐     ┌──────────────┐
            │  selection/   │◄───│  memory/      │  (optional) repair history
            │  (ML model)   │    │  history      │
            └──────┬───────┘     └──────────────┘
                    │ Selected repair operator + priority
                    ▼
            ┌──────────────┐
            │  repair/      │  Apply operator at suspicious location
            └──────┬───────┘
                    │ Candidate repaired circuit
                    ▼
            ┌──────────────┐
            │ verification/ │  Simulate, compare fidelity/distribution
            └──────┬───────┘
                    │ Verified/rejected + repair outcome
                    ▼
              Output: Best repair candidate + verification result
                    │
                    ▼ (feedback)
            ┌──────────────┐
            │  memory/      │  Record (fault_features, operator, outcome)
            └──────────────┘
```

---

## Key Interfaces

### CircuitIR
```python
@dataclass
class CircuitIR:
    circuit: QuantumCircuit   # Original Qiskit circuit
    dag: DAGCircuit           # DAG representation
    num_qubits: int
    depth: int
    gate_list: list[GateInfo] # Ordered list of gates with metadata
```

### FaultFeatureVector
```python
@dataclass
class FaultFeatureVector:
    # Circuit-level features
    num_qubits: int
    circuit_depth: int
    total_gate_count: int
    gate_type_counts: dict[str, int]
    parameter_count: int
    measurement_count: int

    # Local features (at suspected fault location)
    suspect_gate_type: str
    suspect_gate_position: int       # position in gate list
    suspect_gate_depth: int          # depth layer
    suspect_qubit_indices: list[int]
    local_gate_density: float        # gates in neighborhood
    neighboring_gate_types: list[str]
    has_parameters: bool
    is_controlled: bool
    is_entangling: bool

    # Fault-characterization features
    suspiciousness_score: float
    output_deviation: float          # KL divergence or fidelity loss
```

### RepairOperator (enum)
```python
class RepairOperator(Enum):
    GATE_REPLACEMENT = "gate_replacement"
    GATE_INSERTION = "gate_insertion"
    GATE_DELETION = "gate_deletion"
    PARAMETER_MODIFICATION = "parameter_modification"
    QUBIT_REASSIGNMENT = "qubit_reassignment"
    CONTROL_TARGET_SWAP = "control_target_swap"
    GATE_ORDER_SWAP = "gate_order_swap"
    MEASUREMENT_CORRECTION = "measurement_correction"
```

### RepairSelector (abstract)
```python
class RepairSelector(ABC):
    @abstractmethod
    def select(self, features: FaultFeatureVector) -> list[tuple[RepairOperator, float]]:
        \"\"\"Return ranked list of (operator, confidence) tuples.\"\"\"
        pass
```
