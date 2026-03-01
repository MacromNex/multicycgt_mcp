# Step 3: Use Cases Report

## Scan Information
- **Scan Date**: 2026-01-01
- **Filter Applied**: cyclic peptide membrane permeability prediction using MultiCycGT GCN transformer
- **Repository**: Multi_CycGT - A DL-Based Multimodal Model for Membrane Permeability Prediction of Cyclic Peptides
- **Python Version Strategy**: Dual environment (main: 3.10, legacy: 3.9)
- **Environment Strategy**: Main MCP environment + Legacy Multi_CycGT environment

## Repository Analysis

### Key Components Identified
1. **Multi_CycGT Model**: Combines Graph Convolutional Networks (GCN) and Transformer architectures
2. **Data Processing Pipeline**: SMILES and sequence feature extraction
3. **Training Framework**: PyTorch-based deep learning training
4. **Evaluation Metrics**: PAMPA (Parallel Artificial Membrane Permeability Assay) prediction

### Model Architecture
- **GCN Component**: Processes molecular graphs from SMILES representations
- **Transformer Component**: Models amino acid sequences with attention mechanisms
- **Fully Connected Layers**: Combines molecular and sequence features for final prediction

## Use Cases

### UC-001: Membrane Permeability Prediction
- **Description**: Predict PAMPA values for cyclic peptides using molecular and sequence features
- **Script Path**: `examples/use_case_1_predict_membrane_permeability.py`
- **Complexity**: Medium
- **Priority**: High
- **Environment**: `./env` (main MCP environment)
- **Source**: `repo/Multi_CycGT/model/deep_learning/gcn_transformer_fc/model_concat.py`, README.md

**Inputs:**
| Name | Type | Description | Parameter |
|------|------|-------------|----------|
| input_file | CSV file | Peptide data with SMILES, Sequence columns | --input, -i |
| smiles | string | Single SMILES string for prediction | --smiles, -s |
| sequence | string | Amino acid sequence (optional) | --sequence |
| device | string | CPU or CUDA device | --device |

**Outputs:**
| Name | Type | Description |
|------|------|-------------|
| predictions | CSV file | PAMPA predictions with confidence scores |
| console_output | text | Single prediction results |

**Example Usage:**
```bash
# Batch prediction
mamba run -p ./env python examples/use_case_1_predict_membrane_permeability.py --input examples/data/sample_peptides.csv --output results.csv

# Single prediction
mamba run -p ./env python examples/use_case_1_predict_membrane_permeability.py --smiles "CC(C)C[C@@H]1NC(=O)[C@H](Cc2ccccc2)..."
```

**Example Data**: `examples/data/sample_peptides.csv` (12MB, 3000+ peptides), `examples/data/sample_small.csv` (19 peptides)

---

### UC-002: Multi_CycGT Model Training
- **Description**: Train the Multi_CycGT GCN-Transformer model for membrane permeability prediction
- **Script Path**: `examples/use_case_2_train_multicycgt_model.py`
- **Complexity**: Complex
- **Priority**: High
- **Environment**: `./env` (main MCP environment)
- **Source**: `repo/Multi_CycGT/model/deep_learning/gcn_transformer_fc/`, training documentation

**Inputs:**
| Name | Type | Description | Parameter |
|------|------|-------------|----------|
| data | CSV file | Training dataset with PAMPA labels | --data, -d |
| epochs | integer | Number of training epochs | --epochs, -e |
| batch_size | integer | Training batch size | --batch_size, -b |
| learning_rate | float | Learning rate | --learning_rate, -lr |
| test_split | float | Test data fraction | --test_split |
| val_split | float | Validation data fraction | --val_split |
| device | string | Training device (cpu/cuda/auto) | --device |

**Outputs:**
| Name | Type | Description |
|------|------|-------------|
| model_weights | PyTorch file | Trained model parameters |
| training_history | CSV file | Loss and metrics over epochs |
| performance_metrics | console | Test set evaluation results |

**Example Usage:**
```bash
# Full training
mamba run -p ./env python examples/use_case_2_train_multicycgt_model.py --data examples/data/sample_peptides.csv --epochs 100 --batch_size 32

# Quick test training
mamba run -p ./env python examples/use_case_2_train_multicycgt_model.py --data examples/data/sample_small.csv --epochs 5 --batch_size 4
```

**Example Data**: `examples/data/sample_peptides.csv`

---

### UC-003: Peptide Property Analysis
- **Description**: Analyze molecular and sequence properties to understand structure-permeability relationships
- **Script Path**: `examples/use_case_3_analyze_peptide_properties.py`
- **Complexity**: Medium
- **Priority**: Medium
- **Environment**: `./env` (main MCP environment)
- **Source**: Data exploration and analysis of `repo/Multi_CycGT/data_process/`

**Inputs:**
| Name | Type | Description | Parameter |
|------|------|-------------|----------|
| input_file | CSV file | Peptide dataset | --input, -i |
| output_dir | string | Analysis output directory | --output_dir, -o |
| target_column | string | Target column name | --target_column |

**Outputs:**
| Name | Type | Description |
|------|------|-------------|
| property_distributions | PNG | Molecular property histograms |
| correlation_heatmap | PNG | Property correlation matrix |
| permeability_analysis | PNG | PAMPA distribution and relationships |
| pca_analysis | PNG | Principal component analysis |
| analysis_report | Markdown | Summary statistics and insights |
| processed_data | CSV | Enhanced dataset with calculated properties |

**Example Usage:**
```bash
# Full analysis
mamba run -p ./env python examples/use_case_3_analyze_peptide_properties.py --input examples/data/sample_peptides.csv --output_dir analysis/

# Custom target column
mamba run -p ./env python examples/use_case_3_analyze_peptide_properties.py --input examples/data/sample_peptides.csv --target_column Permeability
```

**Example Data**: `examples/data/sample_peptides.csv`

---

## Dataset Analysis

### CycPeptMPDB Dataset
- **Source File**: `repo/Multi_CycGT/data_process/CycPeptMPDB_Peptide_Assay_PAMPA(4).csv`
- **Size**: 12,512,387 bytes (~12 MB)
- **Records**: 3,000+ cyclic peptides
- **Key Columns**:
  - `SMILES`: Chemical structure notation
  - `Sequence`: Amino acid monomer list (e.g., `['L', 'meA', 'L', 'dP', 'meF']`)
  - `Sequence_LogP`: LogP values per monomer
  - `Sequence_TPSA`: TPSA values per monomer
  - `PAMPA`: Membrane permeability target value (-6.0 to -3.0 range)
  - 100+ molecular descriptors (MolWt, LogP, TPSA, etc.)

### Amino Acid Vocabulary
- **Standard amino acids**: A, R, N, D, C, Q, E, G, H, I, L, K, M, F, P, S, T, W, Y, V
- **N-methylated forms**: meA (N-methylalanine), meL (N-methylleucine), meF (N-methylphenylalanine)
- **D-forms**: dP (D-proline), dL (D-leucine)
- **Modified forms**: Me_dL (N-methyl-D-leucine)

## Summary

| Metric | Count |
|--------|-------|
| Total Use Cases Found | 3 |
| Scripts Created | 3 |
| High Priority | 2 |
| Medium Priority | 1 |
| Low Priority | 0 |
| Demo Data Files Copied | 6 |
| Environment Strategy | Dual (main + legacy) |

## Demo Data Index

| Source | Destination | Description | Size |
|--------|-------------|-------------|------|
| `repo/Multi_CycGT/data_process/CycPeptMPDB_Peptide_Assay_PAMPA(4).csv` | `examples/data/sample_peptides.csv` | Full CycPeptMPDB dataset | 12 MB |
| Generated from sample_peptides.csv (head -n 20) | `examples/data/sample_small.csv` | Small test dataset | <1 KB |
| `repo/Multi_CycGT/pred_data/deep_learing/Multi_CycGT/Multi_CycGT_pred_data/experiment_1_predicted_values.csv` | `examples/data/predictions/experiment_1_predicted_values.csv` | Sample prediction results | 10 KB |
| `repo/Multi_CycGT/pred_data/deep_learing/Multi_CycGT/Multi_CycGT_test_result.csv` | `examples/data/predictions/Multi_CycGT_test_result.csv` | Test performance metrics | <1 KB |
| `repo/Multi_CycGT/model/deep_learning/gcn_transformer_fc/vocab.txt` | `examples/data/sequences/vocab.txt` | SMILES vocabulary | <1 KB |

## Architecture Overview

```
Multi_CycGT Model Architecture:
┌─────────────┐    ┌──────────────────┐    ┌─────────────┐
│   SMILES    │───▶│   GCN Encoder    │───▶│             │
│ Molecular   │    │ (Graph Features) │    │             │
│ Graphs      │    └──────────────────┘    │   Fusion    │
└─────────────┘                            │   Layer     │───▶ PAMPA
┌─────────────┐    ┌──────────────────┐    │             │     Prediction
│  Sequence   │───▶│  Transformer     │───▶│             │
│ Amino Acids │    │ (Attention Mech) │    │             │
│ + Features  │    └──────────────────┘    └─────────────┘
└─────────────┘
```

## MCP Integration Opportunities

Based on the analysis, the following MCP tools could be developed:

1. **predict_membrane_permeability** - Single/batch PAMPA prediction
2. **analyze_peptide_properties** - Molecular and sequence analysis
3. **train_custom_model** - Fine-tune models on user data
4. **generate_peptide_variants** - Design peptides with desired properties
5. **evaluate_model_performance** - Assess prediction accuracy

## Technical Notes

- All scripts are designed to work with the main environment (`./env`)
- RDKit functionality uses simplified molecular calculations due to compatibility issues
- PyTorch models use CPU by default (GPU support can be added)
- Sequence features are pre-calculated and stored in the dataset
- SMILES tokenization follows the original Multi_CycGT vocabulary

## Future Enhancements

1. **Docker Integration**: Resolve RDKit compatibility issues
2. **GPU Support**: Add CUDA-enabled training and inference
3. **Model Variants**: Support for other architectures (LSTM, CNN, etc.)
4. **Real-time Inference**: Fast prediction API for single molecules
5. **Interpretability**: Attention visualization and feature importance analysis