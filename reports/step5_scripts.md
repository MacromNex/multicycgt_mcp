# Step 5: Scripts Extraction Report

## Extraction Information
- **Extraction Date**: 2026-01-01
- **Total Scripts**: 3
- **Fully Independent**: 3
- **Repo Dependent**: 0
- **Inlined Functions**: 8
- **Config Files Created**: 3
- **Shared Library Modules**: 3

## Scripts Overview

| Script | Description | Independent | Config | Tested |
|--------|-------------|-------------|--------|--------|
| `predict_membrane_permeability.py` | Predict cyclic peptide membrane permeability | ✅ | `configs/predict_membrane_permeability.json` | ✅ |
| `train_multicycgt_model.py` | Train Multi_CycGT deep learning model | ✅ | `configs/train_multicycgt_model.json` | ✅ |
| `analyze_peptide_properties.py` | Comprehensive peptide property analysis | ✅ | `configs/analyze_peptide_properties.json` | ✅ |

---

## Script Details

### predict_membrane_permeability.py
- **Path**: `scripts/predict_membrane_permeability.py`
- **Source**: `examples/use_case_1_predict_membrane_permeability.py`
- **Description**: Predict membrane permeability (PAMPA) values for cyclic peptides using heuristic model
- **Main Function**: `run_predict_membrane_permeability(input_file, output_file=None, smiles=None, sequence=None, config=None, **kwargs)`
- **Config File**: `configs/predict_membrane_permeability.json`
- **Tested**: ✅ Yes (batch: 19 peptides, single SMILES)
- **Independent of Repo**: ✅ Yes

**Dependencies:**
| Type | Packages/Functions |
|------|-------------------|
| Essential | pandas, numpy, rdkit, torch |
| Inlined | Molecular feature calculation, sequence parsing |
| Repo Required | None |

**Inputs:**
| Name | Type | Format | Description |
|------|------|--------|-------------|
| input_file | file | CSV | Input peptide data with SMILES column |
| smiles | string | SMILES | Single SMILES for prediction |
| sequence | string/list | Amino acids | Optional sequence data |

**Outputs:**
| Name | Type | Format | Description |
|------|------|--------|-------------|
| result | dict/list | - | Prediction results |
| output_file | file | CSV | Enhanced dataset with predictions |

**CLI Usage:**
```bash
python scripts/predict_membrane_permeability.py --input FILE --output FILE
python scripts/predict_membrane_permeability.py --smiles "SMILES_STRING"
```

**Example:**
```bash
python scripts/predict_membrane_permeability.py --input examples/data/sample_small.csv --output results/pred.csv
python scripts/predict_membrane_permeability.py --smiles "CC(C)C[C@@H]1NC(=O)..."
```

**Test Results:**
- ✅ Batch prediction: 19 peptides processed in ~15 seconds
- ✅ Single prediction: PAMPA value -4.5756 (expected range)
- ✅ Output validation: CSV with 19 rows + header, new column added
- ✅ Error handling: Invalid SMILES handled gracefully

---

### train_multicycgt_model.py
- **Path**: `scripts/train_multicycgt_model.py`
- **Source**: `examples/use_case_2_train_multicycgt_model.py`
- **Description**: Train Multi_CycGT GCN-Transformer model for membrane permeability prediction
- **Main Function**: `run_train_multicycgt_model(input_file, output_dir="models", config=None, **kwargs)`
- **Config File**: `configs/train_multicycgt_model.json`
- **Tested**: ✅ Yes (3 epochs on 19 peptides)
- **Independent of Repo**: ✅ Yes

**Dependencies:**
| Type | Packages/Functions |
|------|-------------------|
| Essential | pandas, numpy, torch, sklearn |
| Inlined | Dataset class, model architecture, training loop |
| Repo Required | None |

**Inputs:**
| Name | Type | Format | Description |
|------|------|--------|-------------|
| input_file | file | CSV | Training data with SMILES and PAMPA columns |

**Outputs:**
| Name | Type | Format | Description |
|------|------|--------|-------------|
| model_path | file | .pth | Trained PyTorch model weights |
| history_path | file | CSV | Training metrics per epoch |
| metrics | dict | - | Test set evaluation metrics |

**CLI Usage:**
```bash
python scripts/train_multicycgt_model.py --input FILE --output_dir DIR --epochs N --batch_size N
```

**Example:**
```bash
python scripts/train_multicycgt_model.py --input examples/data/sample_small.csv --epochs 5 --batch_size 4 --output_dir models/
```

**Test Results:**
- ✅ Model training: 461,057 parameters, 3 epochs in ~30 seconds
- ✅ Data split: 12 train, 3 validation, 4 test samples
- ✅ Model file: 1.8MB PyTorch model saved successfully
- ✅ Training history: CSV with loss and R² metrics per epoch
- ✅ Test metrics: RMSE 1.1042 (reasonable for small dataset)

---

### analyze_peptide_properties.py
- **Path**: `scripts/analyze_peptide_properties.py`
- **Source**: `examples/use_case_3_analyze_peptide_properties.py`
- **Description**: Comprehensive analysis of molecular and sequence properties with visualizations
- **Main Function**: `run_analyze_peptide_properties(input_file, output_dir="analysis", target_column=None, config=None, **kwargs)`
- **Config File**: `configs/analyze_peptide_properties.json`
- **Tested**: ✅ Yes (full analysis on 19 peptides)
- **Independent of Repo**: ✅ Yes

**Dependencies:**
| Type | Packages/Functions |
|------|-------------------|
| Essential | pandas, numpy, rdkit, matplotlib, seaborn, sklearn, scipy |
| Inlined | Molecular property calculation, sequence analysis, plotting |
| Repo Required | None |

**Inputs:**
| Name | Type | Format | Description |
|------|------|--------|-------------|
| input_file | file | CSV | Peptide data with SMILES and target column |

**Outputs:**
| Name | Type | Format | Description |
|------|------|--------|-------------|
| output_files | list | - | List of 8 generated files |
| correlations | series | - | Target correlation analysis |
| pca_components | array | - | PCA explained variance |

**Generated Files:**
1. `property_distributions.png` - Molecular property histograms
2. `correlation_heatmap.png` - Feature correlation matrix
3. `target_correlations.png` - Target correlation bar chart
4. `permeability_analysis.png` - Permeability pattern analysis
5. `pca_analysis.png` - PCA explained variance plots
6. `pca_scatter.png` - PCA scatter plot
7. `analysis_report.md` - Statistical summary report
8. `processed_peptide_data.csv` - Enhanced dataset

**CLI Usage:**
```bash
python scripts/analyze_peptide_properties.py --input FILE --output_dir DIR --target_column COL
```

**Example:**
```bash
python scripts/analyze_peptide_properties.py --input examples/data/sample_small.csv --output_dir analysis/
```

**Test Results:**
- ✅ Property calculation: 3 molecular + 23 sequence properties calculated
- ✅ Visualizations: 6 high-resolution plots generated (total ~5MB)
- ✅ Statistical analysis: PCA, correlation analysis, property distributions
- ✅ Report generation: Markdown report with dataset summary
- ✅ Data export: Enhanced CSV with all calculated properties

---

## Shared Library

**Path**: `scripts/lib/`

| Module | Functions | Description | Lines |
|--------|-----------|-------------|-------|
| `molecules.py` | 6 | RDKit molecular operations | 159 |
| `io.py` | 6 | File I/O and configuration | 116 |
| `validation.py` | 5 | Input validation and error checking | 181 |
| `__init__.py` | - | Package initialization and exports | 34 |

**Total Functions**: 17
**Total Lines**: 490

### molecules.py Functions
- `parse_smiles()` - Parse SMILES string to RDKit molecule
- `calculate_molecular_features()` - Calculate molecular descriptors
- `parse_sequence()` - Parse amino acid sequence properties
- `is_cyclic_peptide()` - Check if molecule is cyclic
- `save_molecule()` - Save molecule in various formats

### io.py Functions
- `load_csv_data()` - Load and validate CSV files
- `save_csv_data()` - Save DataFrames to CSV
- `load_config()` - Load JSON configuration files
- `save_config()` - Save configuration to JSON
- `create_output_directory()` - Create output directories
- `save_results_metadata()` - Save execution metadata

### validation.py Functions
- `validate_smiles()` - Validate SMILES strings
- `validate_csv_file()` - Comprehensive CSV validation
- `validate_config()` - Configuration validation
- `validate_file_path()` - File path validation
- `validate_numerical_range()` - Numerical range validation

---

## Configuration Files

### configs/predict_membrane_permeability.json
```json
{
  "device": "cpu",
  "prediction_mode": "heuristic",
  "amino_acid_properties": { ... },
  "heuristic_weights": { ... }
}
```
**Size**: 1.2KB, **Parameters**: 27 amino acid properties + 4 heuristic weights

### configs/train_multicycgt_model.json
```json
{
  "epochs": 100,
  "batch_size": 32,
  "model": { ... },
  "training": { ... },
  "feature_columns": [ ... ]
}
```
**Size**: 0.8KB, **Parameters**: Model architecture + training hyperparameters

### configs/analyze_peptide_properties.json
```json
{
  "target_column": "PAMPA",
  "molecular_properties": [ ... ],
  "amino_acids": { ... },
  "visualization": { ... }
}
```
**Size**: 1.1KB, **Parameters**: Analysis settings + visualization parameters

---

## Dependency Analysis

### Common Dependencies (All Scripts)
| Package | Version | Usage |
|---------|---------|-------|
| pandas | 2.3.1 | Data manipulation |
| numpy | 2.0.2 | Numerical operations |
| rdkit | 2025.03.5 | Molecular operations |

### Script-Specific Dependencies
| Script | Additional Packages |
|--------|-------------------|
| `predict_membrane_permeability.py` | torch (2.0.1+cpu) |
| `train_multicycgt_model.py` | torch, scikit-learn (1.6.1) |
| `analyze_peptide_properties.py` | matplotlib (3.9.4), seaborn, scipy |

### Removed Dependencies
- **Repo imports**: All `sys.path` modifications and repo imports eliminated
- **Hardcoded paths**: All absolute paths converted to relative/configurable
- **Environment-specific code**: Platform-dependent code made portable

---

## Testing Results

### Test Environment
- **Environment**: `./env_py39` (Legacy environment with all ML dependencies)
- **Package Manager**: mamba (preferred over conda)
- **Test Data**: `examples/data/sample_small.csv` (19 peptides)
- **Total Test Time**: ~90 seconds for all scripts

### Individual Script Tests

#### Test 1: Prediction Script
```bash
mamba run -p ./env_py39 python scripts/predict_membrane_permeability.py \
  --input examples/data/sample_small.csv \
  --output results/test_predictions.csv
```
- ✅ **Result**: Success - 19 peptides processed
- ✅ **Output**: CSV file with `Predicted_PAMPA` column
- ✅ **Values**: Range -4.74 to -2.37 (reasonable PAMPA values)
- ✅ **Time**: ~15 seconds

#### Test 2: Training Script
```bash
mamba run -p ./env_py39 python scripts/train_multicycgt_model.py \
  --input examples/data/sample_small.csv \
  --epochs 3 --batch_size 4 \
  --output_dir results/test_model/
```
- ✅ **Result**: Success - Model trained with 461,057 parameters
- ✅ **Output**: Model file (1.8MB) + training history CSV
- ✅ **Metrics**: Final validation loss 1.5295
- ✅ **Time**: ~30 seconds

#### Test 3: Analysis Script
```bash
mamba run -p ./env_py39 python scripts/analyze_peptide_properties.py \
  --input examples/data/sample_small.csv \
  --output_dir results/test_analysis/
```
- ✅ **Result**: Success - 8 files generated
- ✅ **Properties**: 3 molecular + 23 sequence properties calculated
- ✅ **Visualizations**: 6 plots generated (property distributions, correlations, PCA)
- ✅ **Time**: ~45 seconds

#### Test 4: Single SMILES Prediction
```bash
mamba run -p ./env_py39 python scripts/predict_membrane_permeability.py \
  --smiles "CC(C)C[C@@H]1NC(=O)[C@H](Cc2ccccc2)N(C)C(=O)..."
```
- ✅ **Result**: Success - Predicted PAMPA value: -4.5756
- ✅ **Validation**: Value in expected range for cyclic peptide
- ✅ **Time**: <1 second

---

## Script Independence Verification

### Dependencies Check
```bash
# No repo imports found
grep -r "sys.path\|from repo\|import repo" scripts/
# No output - confirmed independent

# No hardcoded paths
grep -r "/home\|/Users\|C:" scripts/
# No output - confirmed portable
```

### Standalone Testing
All scripts tested successfully with:
- ✅ No repo directory access required
- ✅ Only `examples/data/` and `configs/` dependencies
- ✅ All imports from standard packages or shared lib
- ✅ Proper error handling for missing files

---

## Performance Metrics

### Execution Times (19 peptides)
| Script | Time | Throughput |
|--------|------|------------|
| Prediction | 15s | 1.3 peptides/sec |
| Training (3 epochs) | 30s | Model + evaluation |
| Analysis | 45s | Full pipeline + plots |

### Memory Usage
| Script | Peak Memory | Output Size |
|--------|-------------|-------------|
| Prediction | <100MB | 34KB CSV |
| Training | ~200MB | 1.8MB model |
| Analysis | ~150MB | 8 files, ~5MB |

### Scalability
- **Prediction**: Linear scaling with peptide count
- **Training**: Requires 100+ peptides for meaningful models
- **Analysis**: Memory grows quadratically with features for correlation matrix

---

## MCP Readiness

Each script exports a main function ready for MCP wrapping:

### Function Signatures
```python
# predict_membrane_permeability.py
def run_predict_membrane_permeability(
    input_file: Union[str, Path] = None,
    output_file: Optional[Union[str, Path]] = None,
    smiles: Optional[str] = None,
    sequence: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]

# train_multicycgt_model.py
def run_train_multicycgt_model(
    input_file: Union[str, Path],
    output_dir: Optional[Union[str, Path]] = "models",
    config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]

# analyze_peptide_properties.py
def run_analyze_peptide_properties(
    input_file: Union[str, Path],
    output_dir: Optional[Union[str, Path]] = "analysis",
    target_column: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]
```

### Return Format
All functions return standardized dictionaries:
```python
{
    "result": ...,           # Main result (predictions/model/analysis)
    "output_file(s)": ...,   # Path(s) to generated files
    "metadata": {            # Execution metadata
        "input_file": str,
        "config": dict,
        "execution_info": ...
    }
}
```

---

## Success Criteria Verification

- [✅] All 3 verified use cases have corresponding scripts in `scripts/`
- [✅] Each script has a clearly defined main function (e.g., `run_<name>()`)
- [✅] Dependencies minimized - only essential imports (rdkit, numpy, pandas, torch, matplotlib)
- [✅] Repo-specific code eliminated - completely self-contained
- [✅] Configuration externalized to `configs/` directory
- [✅] Scripts work with example data: `python scripts/X.py --input examples/data/Y`
- [✅] `reports/step5_scripts.md` documents all scripts with dependencies
- [✅] Scripts tested and produce correct outputs
- [✅] README.md in `scripts/` explains usage
- [✅] Shared library created for common functions

## Summary

**Step 5 completed successfully** with 3 fully independent, MCP-ready scripts:

1. **predict_membrane_permeability.py** - Heuristic PAMPA prediction
2. **train_multicycgt_model.py** - Deep learning model training
3. **analyze_peptide_properties.py** - Comprehensive property analysis

All scripts are:
- ✅ **Self-contained**: No repo dependencies
- ✅ **Configurable**: External JSON configuration
- ✅ **Tested**: Working with sample data
- ✅ **Documented**: Complete usage instructions
- ✅ **MCP-ready**: Standardized function interfaces

Ready for Step 6: MCP tool wrapping.