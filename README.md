# Multi_CycGT MCP

> MCP tools for cyclic peptide computational analysis using Graph Convolutional Networks and Transformer architectures

## Table of Contents
- [Overview](#overview)
- [Installation](#installation)
- [Local Usage (Scripts)](#local-usage-scripts)
- [MCP Server Installation](#mcp-server-installation)
- [Using with Claude Code](#using-with-claude-code)
- [Using with Gemini CLI](#using-with-gemini-cli)
- [Available Tools](#available-tools)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

## Overview

The Multi_CycGT MCP provides computational tools for analyzing cyclic peptides, specifically focusing on membrane permeability prediction using deep learning models that combine Graph Convolutional Networks (GCN) and Transformer architectures. This MCP server enables natural language interaction with sophisticated cyclic peptide analysis workflows through Claude Code and other MCP-compatible clients.

### Features
- **PAMPA Permeability Prediction**: Predict membrane permeability values for cyclic peptides using SMILES strings or amino acid sequences
- **Deep Learning Model Training**: Train custom Multi_CycGT models on your datasets with GCN-Transformer architecture
- **Comprehensive Property Analysis**: Calculate molecular descriptors, sequence properties, and generate statistical visualizations
- **Batch Processing**: Handle large datasets for virtual screening workflows
- **Job Management**: Submit long-running tasks with progress tracking and result retrieval

### Directory Structure
```
./
├── README.md               # This file
├── env/                    # Main conda environment (Python 3.10)
├── env_py39/               # Legacy environment (Python 3.9)
├── src/
│   ├── mcp_server.py       # FastMCP-compatible MCP server
│   ├── server.py           # CLI server interface
│   └── jobs/               # Job management system
├── scripts/
│   ├── predict_membrane_permeability.py    # PAMPA prediction
│   ├── train_multicycgt_model.py          # Model training
│   ├── analyze_peptide_properties.py      # Property analysis
│   └── lib/                # Shared utilities
├── examples/
│   └── data/               # Demo data
│       ├── sample_peptides.csv        # Full CycPeptMPDB dataset (12MB, 3000+ peptides)
│       ├── sample_small.csv           # Small test dataset (19 peptides)
│       ├── sequences/      # Sample cyclic peptide sequences
│       └── structures/     # Sample 3D structures
├── configs/                # Configuration files
│   ├── predict_membrane_permeability.json
│   ├── train_multicycgt_model.json
│   └── analyze_peptide_properties.json
└── repo/                   # Original Multi_CycGT repository
```

---

## Installation

### Quick Setup

Run the automated setup script:

```bash
./quick_setup.sh
```

This will create the environment and install all dependencies automatically.

### Manual Setup (Advanced)

For manual installation or customization, follow these steps.

#### Prerequisites
- Conda or Mamba (mamba recommended for faster installation)
- Python 3.10+
- Linux/macOS (tested on Ubuntu 20.04+)
- RDKit (installed automatically)

#### Create Environment
Please follow the information in `reports/step3_environment.md` for detailed setup. An example workflow is shown below.

```bash
# Navigate to the MCP directory
cd /home/xux/Desktop/CycPepMCP/CycPepMCP/tool-mcps/multicycgt_mcp

# Check available package manager (prefer mamba over conda)
if command -v mamba &> /dev/null; then
    PKG_MGR="mamba"
else
    PKG_MGR="conda"
fi
echo "Using package manager: $PKG_MGR"

# Create conda environment (use mamba if available)
mamba create -p ./env python=3.10 -y
# or: conda create -p ./env python=3.10 -y

# Activate environment
mamba activate ./env
# or: conda activate ./env

# Install core dependencies
pip install fastmcp loguru pandas numpy tqdm click

# Install PyTorch (CPU version for broader compatibility)
mamba install pytorch torchvision cpuonly -c pytorch -y

# Install RDKit from conda-forge (recommended)
mamba install -c conda-forge rdkit -y

# Install additional ML dependencies
mamba install scikit-learn matplotlib seaborn scipy -y
```

---

## Local Usage (Scripts)

You can use the scripts directly without MCP for local processing.

### Available Scripts

| Script | Description | Example |
|--------|-------------|---------|
| `scripts/predict_membrane_permeability.py` | Predict PAMPA permeability values using heuristic model | See below |
| `scripts/train_multicycgt_model.py` | Train Multi_CycGT GCN-Transformer model | See below |
| `scripts/analyze_peptide_properties.py` | Comprehensive molecular and sequence property analysis | See below |

### Script Examples

#### Predict PAMPA Permeability

```bash
# Activate environment
mamba activate ./env

# Single SMILES prediction
python scripts/predict_membrane_permeability.py \
  --smiles "CC(C)C[C@@H]1NC(=O)[C@H](Cc2ccccc2)N(C)C(=O)[C@H]2CCCN2C(=O)[C@H](CC(C)C)NC(=O)[C@H](C)N(C)C(=O)[C@H](CC(C)C)NC(=O)[C@H](Cc2ccccc2)N(C)C(=O)[C@H]2CCCN2C(=O)[C@H]([C@@H](C)O)NC(=O)[C@H](C)N(C)C1=O"

# Batch prediction
python scripts/predict_membrane_permeability.py \
  --input examples/data/sample_small.csv \
  --output results/predictions.csv

# With custom configuration
python scripts/predict_membrane_permeability.py \
  --input examples/data/sample_small.csv \
  --config configs/predict_membrane_permeability.json \
  --output results/custom_predictions.csv
```

**Parameters:**
- `--smiles, -s`: Cyclic peptide SMILES string (required for single prediction)
- `--input, -i`: Input CSV file with SMILES column (required for batch prediction)
- `--output, -o`: Output file path (default: results/)
- `--sequence`: Optional amino acid sequence (alternative to SMILES)
- `--config`: JSON configuration file

#### Train Multi_CycGT Model

```bash
# Quick training for testing (5 epochs)
python scripts/train_multicycgt_model.py \
  --input examples/data/sample_small.csv \
  --epochs 5 \
  --batch_size 4 \
  --output_dir models/test/

# Production training
python scripts/train_multicycgt_model.py \
  --input examples/data/sample_peptides.csv \
  --epochs 100 \
  --batch_size 32 \
  --learning_rate 0.001 \
  --output_dir models/production/
```

**Parameters:**
- `--input, -i`: CSV file with SMILES and PAMPA columns (required)
- `--epochs, -e`: Number of training epochs (default: 100)
- `--batch_size, -b`: Training batch size (default: 32)
- `--learning_rate, -lr`: Learning rate (default: 0.001)
- `--test_split`: Test data fraction (default: 0.2)
- `--val_split`: Validation data fraction (default: 0.2)
- `--output_dir, -o`: Model output directory (default: models/)

#### Analyze Peptide Properties

```bash
# Full analysis with default settings
python scripts/analyze_peptide_properties.py \
  --input examples/data/sample_small.csv \
  --output_dir analysis/

# Custom target column analysis
python scripts/analyze_peptide_properties.py \
  --input examples/data/sample_peptides.csv \
  --target_column Permeability \
  --output_dir analysis/custom/
```

**Outputs Generated:**
1. `property_distributions.png` - Molecular property histograms
2. `correlation_heatmap.png` - Feature correlation matrix
3. `target_correlations.png` - Target vs properties plots
4. `pca_analysis.png` - PCA loadings plot
5. `pca_scatter.png` - PCA scatter plot
6. `permeability_analysis.png` - Permeability-specific analysis
7. `analysis_report.md` - Statistical summary report
8. `processed_peptide_data.csv` - Enhanced dataset with calculated properties

---

## MCP Server Installation

### Option 1: Using fastmcp (Recommended)

```bash
# Install MCP server for Claude Code
fastmcp install src/mcp_server.py --name cycpep-tools
```

### Option 2: Manual Installation for Claude Code

```bash
# Add MCP server to Claude Code
claude mcp add cycpep-tools -- \
  /home/xux/Desktop/CycPepMCP/CycPepMCP/tool-mcps/multicycgt_mcp/env/bin/python \
  /home/xux/Desktop/CycPepMCP/CycPepMCP/tool-mcps/multicycgt_mcp/src/mcp_server.py

# Verify installation
claude mcp list  # Should show "✓ Connected"
```

### Option 3: Configure in settings.json

Add to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "cycpep-tools": {
      "command": "/home/xux/Desktop/CycPepMCP/CycPepMCP/tool-mcps/multicycgt_mcp/env/bin/python",
      "args": ["/home/xux/Desktop/CycPepMCP/CycPepMCP/tool-mcps/multicycgt_mcp/src/mcp_server.py"]
    }
  }
}
```

---

## Using with Claude Code

After installing the MCP server, you can use it directly in Claude Code.

### Quick Start

```bash
# Start Claude Code
claude
```

### Example Prompts

#### Tool Discovery
```
What tools are available from cycpep-tools?
```

#### Single Peptide Analysis (Fast)
```
Calculate membrane permeability for this cyclic peptide SMILES:
CC(C)C[C@@H]1NC(=O)[C@H](Cc2ccccc2)N(C)C(=O)[C@H]2CCCN2C(=O)[C@H](CC(C)C)NC(=O)[C@H](C)N(C)C(=O)[C@H](CC(C)C)NC(=O)[C@H](Cc2ccccc2)N(C)C(=O)[C@H]2CCCN2C(=O)[C@H]([C@@H](C)O)NC(=O)[C@H](C)N(C)C1=O
```

#### Comprehensive Analysis (Submit API)
```
Submit a comprehensive analysis job for @examples/data/sample_small.csv with job name "small_dataset_analysis"
```

#### Model Training (Submit API)
```
Submit a model training job for @examples/data/sample_small.csv with 10 epochs and batch size 4, name it "test_training"
```

#### Check Job Status
```
Check the status of job abc12345
```

#### Batch Processing
```
Calculate PAMPA permeability for all peptides in @examples/data/sample_small.csv and save results to @results/batch_predictions.csv
```

### Using @ References

In Claude Code, use `@` to reference files and directories:

| Reference | Description |
|-----------|-------------|
| `@examples/data/sample_small.csv` | Reference the small test dataset |
| `@examples/data/sample_peptides.csv` | Reference the full CycPeptMPDB dataset |
| `@configs/predict_membrane_permeability.json` | Reference a config file |
| `@results/` | Reference output directory |

---

## Using with Gemini CLI

### Configuration

Add to `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "cycpep-tools": {
      "command": "/home/xux/Desktop/CycPepMCP/CycPepMCP/tool-mcps/multicycgt_mcp/env/bin/python",
      "args": ["/home/xux/Desktop/CycPepMCP/CycPepMCP/tool-mcps/multicycgt_mcp/src/mcp_server.py"]
    }
  }
}
```

### Example Prompts

```bash
# Start Gemini CLI
gemini

# Example prompts (same as Claude Code)
> What tools are available?
> Calculate permeability for cyclic peptide cyclo(GRGDSP)
```

---

## Available Tools

### Quick Operations (Sync API)

These tools return results immediately (< 10 minutes):

| Tool | Description | Parameters |
|------|-------------|------------|
| `predict_membrane_permeability` | Calculate PAMPA permeability values | `smiles`, `sequence`, `input_file`, `output_file`, `config_file` |

### Long-Running Tasks (Submit API)

These tools return a job_id for tracking (> 10 minutes):

| Tool | Description | Parameters |
|------|-------------|------------|
| `submit_peptide_analysis` | Comprehensive property analysis with visualizations | `input_file`, `output_dir`, `target_column`, `config_file`, `job_name` |
| `submit_model_training` | Train Multi_CycGT GCN-Transformer model | `input_file`, `output_dir`, `epochs`, `batch_size`, `learning_rate`, `test_split`, `val_split`, `config_file`, `job_name` |

### Job Management Tools

| Tool | Description |
|------|-------------|
| `get_job_status` | Check job progress and timestamps |
| `get_job_result` | Get results when completed |
| `get_job_log` | View execution logs |
| `cancel_job` | Cancel running job |
| `list_jobs` | List all jobs with optional status filter |

---

## Examples

### Example 1: Quick Permeability Prediction

**Goal:** Calculate PAMPA permeability for a cyclic peptide

**Using Script:**
```bash
mamba activate ./env
python scripts/predict_membrane_permeability.py \
  --smiles "CC(C)C[C@@H]1NC(=O)[C@H](Cc2ccccc2)N(C)C(=O)[C@H]2CCCN2C(=O)[C@H](CC(C)C)NC(=O)[C@H](C)N(C)C(=O)[C@H](CC(C)C)NC(=O)[C@H](Cc2ccccc2)N(C)C(=O)[C@H]2CCCN2C(=O)[C@H]([C@@H](C)O)NC(=O)[C@H](C)N(C)C1=O"
```

**Using MCP (in Claude Code):**
```
Calculate membrane permeability for cyclic peptide SMILES: CC(C)C[C@@H]1NC(=O)[C@H](Cc2ccccc2)...
```

**Expected Output:**
- PAMPA value: approximately -3.9 (range: -6.0 to -3.0)
- Lower values indicate lower permeability

### Example 2: Comprehensive Dataset Analysis

**Goal:** Analyze molecular and sequence properties with visualizations

**Using Script:**
```bash
mamba activate ./env
python scripts/analyze_peptide_properties.py \
  --input examples/data/sample_small.csv \
  --output_dir analysis/sample_analysis/
```

**Using MCP (in Claude Code):**
```
Submit comprehensive analysis for @examples/data/sample_small.csv with output directory "analysis_results" and job name "sample_analysis"

When the job completes, show me the generated files and key findings from the analysis report.
```

**Expected Output:**
- 8 files generated: 6 visualizations + report + enhanced dataset
- Analysis includes molecular properties (MolWt, LogP, TPSA), sequence properties, correlations, PCA
- Runtime: ~20-45 seconds for 19 peptides

### Example 3: Model Training Pipeline

**Goal:** Train a custom Multi_CycGT model on sample data

**Using Script:**
```bash
mamba activate ./env
python scripts/train_multicycgt_model.py \
  --input examples/data/sample_small.csv \
  --epochs 10 \
  --batch_size 4 \
  --output_dir models/sample_model/
```

**Using MCP (in Claude Code):**
```
Submit model training for @examples/data/sample_small.csv with these parameters:
- epochs: 10
- batch_size: 4
- learning_rate: 0.001
- job_name: "sample_model_training"

Monitor the training progress and show me the final metrics when complete.
```

**Expected Output:**
- PyTorch model file (~1.8MB): `multicycgt_final.pth`
- Training history CSV with loss and metrics per epoch
- Test set evaluation: RMSE and R² scores

### Example 4: Virtual Screening Workflow

**Goal:** Screen a library of cyclic peptides for membrane permeability

**Using MCP (in Claude Code):**
```
I want to screen these cyclic peptides for oral bioavailability potential:

First, predict PAMPA permeability for all peptides in @examples/data/sample_small.csv

Then, identify peptides with:
- PAMPA > -4.0 (better permeability)
- Show me the top 5 candidates with their SMILES and predicted values

Finally, submit a detailed analysis for these top candidates.
```

---

## Demo Data

The `examples/data/` directory contains sample data for testing:

| File | Description | Size | Peptides | Use With |
|------|-------------|------|----------|----------|
| `sample_peptides.csv` | Full CycPeptMPDB dataset | 12MB | 3000+ | All tools (production) |
| `sample_small.csv` | Small test dataset | 33KB | 19 | All tools (testing) |
| `sequences/vocab.txt` | SMILES vocabulary | <1KB | - | Reference |

### Sample Data Format

The CSV files contain these key columns:
- `SMILES`: Chemical structure notation for cyclic peptides
- `Sequence`: Amino acid sequence (e.g., `['L', 'meA', 'L', 'dP', 'meF']`)
- `PAMPA`: Membrane permeability target value (-6.0 to -3.0 range)
- `MolWt`, `LogP`, `TPSA`: Molecular descriptors
- 100+ additional molecular descriptors for analysis

---

## Configuration Files

The `configs/` directory contains configuration templates:

| Config | Description | Parameters |
|--------|-------------|------------|
| `predict_membrane_permeability.json` | Permeability prediction settings | amino acid properties, heuristic weights |
| `train_multicycgt_model.json` | Model training config | architecture, hyperparameters |
| `analyze_peptide_properties.json` | Analysis settings | properties list, visualization parameters |

### Config Example

```json
{
  "amino_acid_properties": {
    "A": {"logp": 0.31, "tpsa": 43.09},
    "F": {"logp": 1.79, "tpsa": 43.09},
    "meA": {"logp": 0.1354, "tpsa": 20.31}
  },
  "heuristic_weights": {
    "mol_wt": -0.001,
    "tpsa": -0.01,
    "logp": 0.5,
    "base": -2.0
  }
}
```

---

## Troubleshooting

### Environment Issues

**Problem:** Environment not found
```bash
# Recreate environment
mamba create -p ./env python=3.10 -y
mamba activate ./env
pip install fastmcp loguru pandas numpy
mamba install pytorch cpuonly -c pytorch -y
mamba install -c conda-forge rdkit -y
```

**Problem:** RDKit import errors
```bash
# Install RDKit from conda-forge (recommended)
mamba install -c conda-forge rdkit -y

# Alternative: install via pip (less reliable)
pip install rdkit
```

**Problem:** PyTorch not found
```bash
# Install CPU version of PyTorch
mamba install pytorch cpuonly -c pytorch -y
```

**Problem:** Import errors
```bash
# Verify installation
python -c "import rdkit; import torch; import pandas; import numpy; print('All dependencies available')"
```

### MCP Issues

**Problem:** Server not found in Claude Code
```bash
# Check MCP registration
claude mcp list

# Re-add if needed
claude mcp remove cycpep-tools
claude mcp add cycpep-tools -- \
  /home/xux/Desktop/CycPepMCP/CycPepMCP/tool-mcps/multicycgt_mcp/env/bin/python \
  /home/xux/Desktop/CycPepMCP/CycPepMCP/tool-mcps/multicycgt_mcp/src/mcp_server.py
```

**Problem:** Invalid SMILES error
```
Ensure your SMILES string is valid for cyclic peptides.
Example valid SMILES: CC(C)C[C@@H]1NC(=O)...
The SMILES should represent a properly closed ring structure.
```

**Problem:** Tools not working
```bash
# Test server directly
python src/server.py --list-tools
# Should show 8 tools

# Test a simple prediction
python src/server.py --tool predict_membrane_permeability \
  --args '{"smiles": "CC(=O)NC1CCCC1C(=O)O"}'
```

### Job Issues

**Problem:** Job stuck in pending
```bash
# Check job directory
ls -la jobs/

# View job log
python src/server.py --tool get_job_log --args '{"job_id": "JOB_ID"}'
```

**Problem:** Job failed
```
Use get_job_log with job_id "JOB_ID" and tail 100 to see error details
Check that input files exist and are properly formatted
```

**Problem:** Out of memory during training
```bash
# Reduce batch size in training
python scripts/train_multicycgt_model.py --batch_size 4 --epochs 10

# Or use smaller dataset
python scripts/train_multicycgt_model.py \
  --input examples/data/sample_small.csv
```

### Data Issues

**Problem:** CSV file not found
```bash
# Verify file exists
ls -la examples/data/sample_small.csv

# Check file format
head examples/data/sample_small.csv
```

**Problem:** Missing SMILES column
```
Ensure your CSV file has a column named 'SMILES' with valid SMILES strings
Example format: CycPeptMPDB_ID,SMILES,PAMPA,...
```

---

## Development

### Running Tests

```bash
# Activate environment
mamba activate ./env

# Test individual scripts
python scripts/predict_membrane_permeability.py \
  --input examples/data/sample_small.csv

# Test MCP server
python src/server.py --list-tools
```

### Starting Dev Server

```bash
# Run MCP server in development mode
python src/mcp_server.py
```

### Performance Monitoring

| Operation | Small Dataset (19 peptides) | Large Dataset (3000+ peptides) |
|-----------|------------------------------|----------------------------------|
| Permeability Prediction | ~15 seconds | ~20 minutes |
| Property Analysis | ~45 seconds | ~5-15 minutes |
| Model Training (10 epochs) | ~30 seconds | ~30-60 minutes |

---

## License

Based on [Multi_CycGT](https://github.com/ChunhuaLab/Multi_CycGT) - A DL-Based Multimodal Model for Membrane Permeability Prediction of Cyclic Peptides

## Credits

- **Original Model**: Multi_CycGT by ChunhuaLab
- **Dataset**: CycPeptMPDB (Cyclic Peptide Membrane Permeability Database)
- **Architecture**: Graph Convolutional Networks + Transformer
- **MCP Implementation**: Claude Code compatible server