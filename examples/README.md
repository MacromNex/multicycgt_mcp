# Multi_CycGT Examples

This directory contains example scripts and demo data for the Multi_CycGT MCP server. These examples demonstrate core functionality for cyclic peptide membrane permeability prediction using the Multi_CycGT deep learning framework.

## Use Case Scripts

### 1. Membrane Permeability Prediction
**File**: `use_case_1_predict_membrane_permeability.py`
**Description**: Predict PAMPA (membrane permeability) values for cyclic peptides

```bash
# Predict for a dataset
mamba run -p ../env python use_case_1_predict_membrane_permeability.py --input data/sample_small.csv

# Predict for a single SMILES
mamba run -p ../env python use_case_1_predict_membrane_permeability.py --smiles "CC(C)C[C@@H]1NC(=O)..."
```

**Input**: CSV file with SMILES and/or Sequence columns
**Output**: Predicted PAMPA values (negative = low permeability)

### 2. Model Training
**File**: `use_case_2_train_multicycgt_model.py`
**Description**: Train the Multi_CycGT GCN-Transformer model

```bash
# Quick test training
mamba run -p ../env python use_case_2_train_multicycgt_model.py --data data/sample_small.csv --epochs 5

# Full training
mamba run -p ../env python use_case_2_train_multicycgt_model.py --data data/sample_peptides.csv --epochs 100
```

**Input**: Training dataset with PAMPA labels
**Output**: Trained model weights and performance metrics

### 3. Property Analysis
**File**: `use_case_3_analyze_peptide_properties.py`
**Description**: Analyze molecular and sequence properties

```bash
# Generate analysis plots and report
mamba run -p ../env python use_case_3_analyze_peptide_properties.py --input data/sample_peptides.csv --output_dir analysis/
```

**Input**: Peptide dataset
**Output**: Plots, correlations, PCA analysis, and summary report

## Demo Data

### Peptide Datasets
- **`data/sample_peptides.csv`** - Full CycPeptMPDB dataset (~3000 peptides, 12MB)
- **`data/sample_small.csv`** - Small test dataset (19 peptides, <1KB)

### Data Subdirectories
- **`data/sequences/`** - Vocabulary files and sequence data
- **`data/structures/`** - 3D structure files (placeholder)
- **`data/models/`** - Pre-trained model weights (placeholder)
- **`data/predictions/`** - Sample prediction results

### Sample Data Format

The CSV files contain the following key columns:

```
CycPeptMPDB_ID,SMILES,Sequence,Sequence_LogP,Sequence_TPSA,PAMPA,MolWt,MolLogP,TPSA,NumHDonors,NumHAcceptors,...
```

**Example row**:
- `SMILES`: `CC(C)C[C@@H]1NC(=O)[C@H](Cc2ccccc2)N(C)C(=O)...`
- `Sequence`: `['L', 'meA', 'L', 'dP', 'meF', 'L', 'meA', 'T', 'dP', 'meF']`
- `Sequence_LogP`: `[0.8194, 0.1354, 0.8194, 0.2795, 1.3582, ...]`
- `Sequence_TPSA`: `[29.1, 20.31, 29.1, 20.31, 20.31, ...]`
- `PAMPA`: `-3.9` (target membrane permeability)

### Amino Acid Codes

The dataset uses both standard and modified amino acids:

| Code | Name | LogP | TPSA |
|------|------|------|------|
| L | Leucine | 0.8194 | 29.1 |
| meA | N-methylalanine | 0.1354 | 20.31 |
| dP | D-proline | 0.2795 | 20.31 |
| meF | N-methylphenylalanine | 1.3582 | 20.31 |
| meL | N-methylleucine | 1.1616 | 20.31 |
| T | Threonine | -0.1918 | 38.33 |
| F | Phenylalanine | 1.016 | 29.1 |
| dL | D-leucine | 0.8194 | 29.1 |
| Me_dL | N-methyl-D-leucine | 1.1616 | 20.31 |

## Running the Examples

### Prerequisites
```bash
# Activate the main environment
mamba activate ./env  # or: mamba activate /path/to/multicycgt_mcp/env
```

### Quick Start
```bash
# Navigate to examples directory
cd examples/

# Test with small dataset
mamba run -p ../env python use_case_1_predict_membrane_permeability.py --input data/sample_small.csv

# Analyze properties
mamba run -p ../env python use_case_3_analyze_peptide_properties.py --input data/sample_small.csv --output_dir test_analysis/
```

### Expected Outputs

**Prediction Script**:
```
Loading peptide data from: data/sample_small.csv
Loaded 19 peptides
Running membrane permeability predictions...
Predictions saved to: predictions.csv

Prediction Summary:
  Mean PAMPA: -4.2156
  Std PAMPA:  0.7834
  Min PAMPA:  -5.8912
  Max PAMPA:  -2.9876
```

**Training Script**:
```
Loaded 19 samples
Model initialized with 89,345 parameters
Training Multi_CycGT model for 5 epochs...
Epoch 5/5: Train Loss: 0.1234, Val Loss: 0.2345, Val R²: 0.7890
Training completed! Best validation loss: 0.1890
```

**Analysis Script**:
```
Generated files:
  - property_distributions.png
  - correlation_heatmap.png
  - permeability_analysis.png
  - pca_analysis.png
  - analysis_report.md
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you're using the correct environment
   ```bash
   mamba run -p ../env python script.py  # Use this format
   ```

2. **File Not Found**: Check that you're in the examples/ directory
   ```bash
   pwd  # Should end with /examples
   ls data/  # Should show CSV files
   ```

3. **Memory Issues**: Use `sample_small.csv` for testing
   ```bash
   # Instead of sample_peptides.csv, use:
   python script.py --input data/sample_small.csv
   ```

4. **RDKit Warnings**: These are expected due to environment limitations
   ```
   RDKit ERROR: [molecule processing warnings]  # Safe to ignore
   ```

### Performance Notes

- **Small dataset** (`sample_small.csv`): ~1 second processing time
- **Full dataset** (`sample_peptides.csv`): ~30 seconds processing time
- **Training**: 5 epochs take ~10 seconds on sample_small.csv
- **Analysis**: Full analysis takes ~20 seconds for sample_peptides.csv

## Development

To add new examples:

1. Follow the existing script structure
2. Use argparse for command-line arguments
3. Include proper error handling and progress indicators
4. Test with both small and large datasets
5. Document inputs, outputs, and example usage

## Data Sources

- **Original Dataset**: CycPeptMPDB - Cyclic Peptide Membrane Permeability Database
- **Model Architecture**: Multi_CycGT - GCN + Transformer for peptide property prediction
- **Molecular Descriptors**: RDKit-calculated properties
- **Sequence Features**: Pre-calculated LogP and TPSA values per amino acid

For more information, see the main README.md file in the project root.