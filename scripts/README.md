# MCP Scripts

Clean, self-contained scripts extracted from use cases for MCP tool wrapping.

## Design Principles

1. **Minimal Dependencies**: Only essential packages imported (rdkit, numpy, pandas, torch, matplotlib)
2. **Self-Contained**: Functions inlined where possible, repo dependencies eliminated
3. **Configurable**: Parameters in config files, not hardcoded
4. **MCP-Ready**: Each script has a main function ready for MCP wrapping

## Scripts Overview

| Script | Description | Independent | Config | Tested |
|--------|-------------|-------------|--------|--------|
| `predict_membrane_permeability.py` | Predict PAMPA values for cyclic peptides | ✅ Yes | ✅ | ✅ |
| `train_multicycgt_model.py` | Train Multi_CycGT deep learning model | ✅ Yes | ✅ | ✅ |
| `analyze_peptide_properties.py` | Analyze molecular/sequence properties | ✅ Yes | ✅ | ✅ |

## Installation and Setup

```bash
# Activate the legacy environment (has all required dependencies)
mamba activate ./env_py39  # or: conda activate ./env_py39

# Test that dependencies are available
python -c "import rdkit, torch, sklearn, matplotlib; print('All dependencies available')"
```

## Usage Examples

### 1. Membrane Permeability Prediction

```bash
# Batch prediction
python scripts/predict_membrane_permeability.py \
  --input examples/data/sample_small.csv \
  --output results/predictions.csv

# Single SMILES prediction
python scripts/predict_membrane_permeability.py \
  --smiles "CC(C)C[C@@H]1NC(=O)..."

# With custom config
python scripts/predict_membrane_permeability.py \
  --input data.csv \
  --output predictions.csv \
  --config configs/predict_membrane_permeability.json
```

**Expected Output:**
- Batch: CSV file with `Predicted_PAMPA` column added
- Single: Printed PAMPA value (negative = low permeability)

### 2. Model Training

```bash
# Quick training for testing
python scripts/train_multicycgt_model.py \
  --input examples/data/sample_small.csv \
  --epochs 5 \
  --batch_size 4 \
  --output_dir models/

# Production training
python scripts/train_multicycgt_model.py \
  --input data/large_training_set.csv \
  --epochs 100 \
  --batch_size 32 \
  --output_dir production_models/
```

**Expected Output:**
- `models/multicycgt_final.pth` - Trained model weights
- `models/training_history.csv` - Training metrics per epoch

### 3. Property Analysis

```bash
# Full analysis with visualizations
python scripts/analyze_peptide_properties.py \
  --input examples/data/sample_small.csv \
  --output_dir analysis/

# Custom target column
python scripts/analyze_peptide_properties.py \
  --input data.csv \
  --target_column Permeability \
  --output_dir analysis/
```

**Expected Output:**
- 6 visualization PNG files (distributions, correlations, PCA, etc.)
- `analysis_report.md` - Statistical summary
- `processed_peptide_data.csv` - Dataset with calculated properties

## Shared Library

Common functions are available in `scripts/lib/`:

```python
from scripts.lib import parse_smiles, load_csv_data, validate_smiles

# Parse SMILES
mol = parse_smiles("CC(C)C[C@@H]1NC(=O)...")

# Load data with validation
data = load_csv_data(Path("data.csv"), required_columns=["SMILES"])

# Validate SMILES
is_valid = validate_smiles("CC(C)C...")
```

### Library Modules

- **`molecules.py`**: RDKit molecular operations, SMILES parsing, property calculation
- **`io.py`**: File loading/saving, configuration handling
- **`validation.py`**: Input validation, error checking

## Configuration Files

Each script can use a JSON configuration file in `configs/`:

- `configs/predict_membrane_permeability.json` - Amino acid properties, heuristic weights
- `configs/train_multicycgt_model.json` - Model architecture, training hyperparameters
- `configs/analyze_peptide_properties.json` - Analysis settings, visualization parameters

Example config usage:
```bash
python scripts/predict_membrane_permeability.py \
  --input data.csv \
  --config configs/custom_prediction.json
```

## For MCP Wrapping (Step 6)

Each script exports a main function that can be wrapped as an MCP tool:

```python
# Import the main function
from scripts.predict_membrane_permeability import run_predict_membrane_permeability

# In MCP server:
@mcp.tool()
def predict_cyclic_peptide_permeability(
    input_file: str,
    output_file: str = None,
    smiles: str = None
) -> Dict[str, Any]:
    \"\"\"Predict membrane permeability for cyclic peptides\"\"\"
    return run_predict_membrane_permeability(
        input_file=input_file,
        output_file=output_file,
        smiles=smiles
    )
```

## Testing and Validation

All scripts have been tested with sample data:

```bash
# Test prediction script
python scripts/predict_membrane_permeability.py \
  --input examples/data/sample_small.csv \
  --output results/test_predictions.csv
# ✅ SUCCESS: 19 peptides processed, predictions saved

# Test training script
python scripts/train_multicycgt_model.py \
  --input examples/data/sample_small.csv \
  --epochs 3 --batch_size 4 \
  --output_dir results/test_model/
# ✅ SUCCESS: Model trained, 461,057 parameters

# Test analysis script
python scripts/analyze_peptide_properties.py \
  --input examples/data/sample_small.csv \
  --output_dir results/test_analysis/
# ✅ SUCCESS: 8 files generated (plots, report, data)
```

## Dependencies

### Essential (All Scripts)
- **pandas** - Data manipulation
- **numpy** - Numerical operations
- **rdkit** - Molecular operations

### ML Scripts (train_multicycgt_model.py)
- **torch** - Deep learning framework
- **scikit-learn** - Model evaluation metrics

### Analysis Script (analyze_peptide_properties.py)
- **matplotlib** - Plotting
- **seaborn** - Statistical visualizations
- **scipy** - Statistical functions

### Notes

- All scripts work with the legacy environment `./env_py39`
- No repo dependencies - completely self-contained
- Scripts handle invalid SMILES gracefully (NaN values)
- Progress indicators show processing status
- All file I/O includes proper error handling
- Configurations can override any default parameter

## Performance

Tested performance on sample data (19 peptides):

| Script | Execution Time | Memory Usage | Output Size |
|--------|----------------|---------------|-------------|
| Prediction | ~15 seconds | Low | 34KB CSV |
| Training (5 epochs) | ~30 seconds | Medium | 1.8MB model |
| Analysis | ~45 seconds | Medium | 8 files, ~5MB |

For production use:
- Prediction: Scales linearly with number of peptides
- Training: Requires 100+ peptides for meaningful models
- Analysis: Memory usage grows with dataset size for correlation matrices