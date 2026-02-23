#!/usr/bin/env python3
"""
Script: predict_membrane_permeability.py
Description: Predict membrane permeability (PAMPA) values for cyclic peptides using simplified Multi_CycGT model

Original Use Case: examples/use_case_1_predict_membrane_permeability.py
Dependencies Removed: None (script was already self-contained)

Usage:
    python scripts/predict_membrane_permeability.py --input <input_file> --output <output_file>

Example:
    python scripts/predict_membrane_permeability.py --input examples/data/sample_small.csv --output results/predictions.csv
"""

# ==============================================================================
# Minimal Imports (only essential packages)
# ==============================================================================
import argparse
from pathlib import Path
from typing import Union, Optional, Dict, Any, List
import json
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from rdkit import Chem
from rdkit.Chem import Descriptors
import warnings

warnings.filterwarnings('ignore')

# ==============================================================================
# Configuration (extracted from use case)
# ==============================================================================
DEFAULT_CONFIG = {
    "device": "cpu",
    "prediction_mode": "heuristic",  # Could be "heuristic" or "model" if we had trained model
    "amino_acid_properties": {
        'A': {'logp': 0.31, 'tpsa': 43.09}, 'R': {'logp': -1.01, 'tpsa': 125.22},
        'N': {'logp': -0.6, 'tpsa': 92.42}, 'D': {'logp': -0.77, 'tpsa': 83.55},
        'C': {'logp': 0.24, 'tpsa': 44.76}, 'Q': {'logp': -0.22, 'tpsa': 105.15},
        'E': {'logp': -0.64, 'tpsa': 96.28}, 'G': {'logp': 0.0, 'tpsa': 43.09},
        'H': {'logp': -0.07, 'tpsa': 68.13}, 'I': {'logp': 0.73, 'tpsa': 43.09},
        'L': {'logp': 0.73, 'tpsa': 43.09}, 'K': {'logp': -0.99, 'tpsa': 102.78},
        'M': {'logp': 0.26, 'tpsa': 54.37}, 'F': {'logp': 1.79, 'tpsa': 43.09},
        'P': {'logp': 0.72, 'tpsa': 32.34}, 'S': {'logp': -0.04, 'tpsa': 63.32},
        'T': {'logp': 0.26, 'tpsa': 63.32}, 'W': {'logp': 2.25, 'tpsa': 56.17},
        'Y': {'logp': 0.96, 'tpsa': 63.32}, 'V': {'logp': 0.54, 'tpsa': 43.09},
        # Custom monomers from Multi_CycGT
        'meA': {'logp': 0.1354, 'tpsa': 20.31}, 'meL': {'logp': 1.1616, 'tpsa': 20.31},
        'dP': {'logp': 0.2795, 'tpsa': 20.31}, 'meF': {'logp': 1.3582, 'tpsa': 20.31},
        'dL': {'logp': 0.8194, 'tpsa': 29.1}, 'Me_dL': {'logp': 1.1616, 'tpsa': 20.31}
    },
    "heuristic_weights": {
        "mol_wt": -0.001,
        "tpsa": -0.01,
        "logp": 0.5,
        "base": -2.0
    }
}

# ==============================================================================
# Inlined Utility Functions (simplified from use case)
# ==============================================================================
def parse_smiles(smiles: str) -> Optional[Chem.Mol]:
    """Parse SMILES string to RDKit molecule. Inlined from use case."""
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError(f"Invalid SMILES: {smiles}")
        return mol
    except Exception as e:
        print(f"Error processing SMILES {smiles}: {e}")
        return None

def calculate_molecular_features(mol: Chem.Mol) -> Dict[str, float]:
    """Calculate molecular descriptors for RDKit molecule."""
    return {
        'MolWt': Descriptors.MolWt(mol),
        'LogP': Descriptors.MolLogP(mol),
        'TPSA': Descriptors.TPSA(mol),
        'NumHDonors': Descriptors.NumHDonors(mol),
        'NumHAcceptors': Descriptors.NumHAcceptors(mol),
        'NumRotatableBonds': Descriptors.NumRotatableBonds(mol),
        'HeavyAtomCount': mol.GetNumHeavyAtoms(),
        'RingCount': Descriptors.RingCount(mol)
    }

def parse_sequence(sequence: Union[str, List[str]], aa_properties: Dict) -> Dict[str, Any]:
    """Parse amino acid sequence and calculate properties."""
    if isinstance(sequence, str):
        # Parse sequence string to list
        sequence = eval(sequence) if sequence.startswith('[') else list(sequence)

    logp_values = []
    tpsa_values = []

    for aa in sequence:
        if aa in aa_properties:
            logp_values.append(aa_properties[aa]['logp'])
            tpsa_values.append(aa_properties[aa]['tpsa'])
        else:
            # Default values for unknown amino acids
            logp_values.append(0.0)
            tpsa_values.append(43.09)

    return {
        'sequence_logp': logp_values,
        'sequence_tpsa': tpsa_values,
        'length': len(sequence)
    }

def predict_permeability_heuristic(mol_features: Dict, seq_features: Dict, weights: Dict) -> float:
    """Simple heuristic prediction based on molecular properties."""
    # Use molecular features if available, otherwise sequence-derived values
    logp = mol_features.get('LogP', np.mean(seq_features['sequence_logp']) if seq_features['sequence_logp'] else 0)
    tpsa = mol_features.get('TPSA', np.mean(seq_features['sequence_tpsa']) if seq_features['sequence_tpsa'] else 0)
    mol_wt = mol_features.get('MolWt', seq_features['length'] * 100)  # Approximate

    # Simplified permeability prediction (negative values indicate low permeability)
    predicted_pampa = (weights["mol_wt"] * mol_wt +
                      weights["tpsa"] * tpsa +
                      weights["logp"] * logp +
                      weights["base"])

    return float(predicted_pampa)

def load_input_data(file_path: Path) -> Optional[pd.DataFrame]:
    """Load peptide data from CSV file."""
    try:
        df = pd.read_csv(file_path)
        required_columns = ['SMILES']

        for col in required_columns:
            if col not in df.columns:
                print(f"Warning: Required column '{col}' not found in input file")

        print(f"Loaded {len(df)} peptides from {file_path}")
        return df
    except Exception as e:
        print(f"Error loading data from {file_path}: {e}")
        return None

def save_predictions(data: pd.DataFrame, predictions: List[float], output_path: Path) -> None:
    """Save predictions to CSV file."""
    data_copy = data.copy()
    data_copy['Predicted_PAMPA'] = predictions
    data_copy.to_csv(output_path, index=False)

# ==============================================================================
# Core Function (main logic extracted from use case)
# ==============================================================================
def run_predict_membrane_permeability(
    input_file: Union[str, Path] = None,
    output_file: Optional[Union[str, Path]] = None,
    smiles: Optional[str] = None,
    sequence: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Main function for cyclic peptide membrane permeability prediction.

    Args:
        input_file: Path to input CSV file with SMILES column
        output_file: Path to save output predictions (optional)
        smiles: Single SMILES string for prediction
        sequence: Single amino acid sequence for prediction
        config: Configuration dict (uses DEFAULT_CONFIG if not provided)
        **kwargs: Override specific config parameters

    Returns:
        Dict containing:
            - result: Prediction result(s)
            - output_file: Path to output file (if saved)
            - metadata: Execution metadata

    Example:
        >>> # Batch prediction
        >>> result = run_predict_membrane_permeability("input.csv", "output.csv")
        >>> print(result['output_file'])

        >>> # Single SMILES prediction
        >>> result = run_predict_membrane_permeability(smiles="CC(C)C[C@@H]1NC(=O)...")
        >>> print(result['result'])
    """
    # Setup configuration
    config = {**DEFAULT_CONFIG, **(config or {}), **kwargs}

    # Single prediction mode
    if smiles:
        mol = parse_smiles(smiles)
        if mol is None:
            return {"result": None, "error": "Invalid SMILES"}

        mol_features = calculate_molecular_features(mol)
        seq_features = parse_sequence(sequence, config["amino_acid_properties"]) if sequence else {'sequence_logp': [], 'sequence_tpsa': [], 'length': 0}

        prediction = predict_permeability_heuristic(mol_features, seq_features, config["heuristic_weights"])

        return {
            "result": prediction,
            "output_file": None,
            "metadata": {
                "mode": "single",
                "smiles": smiles,
                "sequence": sequence,
                "config": config
            }
        }

    # Batch prediction mode
    if not input_file:
        raise ValueError("Either input_file or smiles must be provided")

    input_file = Path(input_file)
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    # Load data
    data = load_input_data(input_file)
    if data is None:
        raise ValueError(f"Could not load data from {input_file}")

    # Process predictions
    predictions = []
    for idx, row in data.iterrows():
        smiles_val = row.get('SMILES', None)
        sequence_val = row.get('Sequence', None)

        if smiles_val:
            mol = parse_smiles(smiles_val)
            if mol is None:
                predictions.append(None)
                continue

            mol_features = calculate_molecular_features(mol)
        else:
            mol_features = {}

        if sequence_val:
            seq_features = parse_sequence(sequence_val, config["amino_acid_properties"])
        else:
            seq_features = {'sequence_logp': [], 'sequence_tpsa': [], 'length': 0}

        pred = predict_permeability_heuristic(mol_features, seq_features, config["heuristic_weights"])
        predictions.append(pred)

        print(f"Processed peptide {idx + 1}/{len(data)}")

    # Save output if requested
    output_path = None
    if output_file:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        save_predictions(data, predictions, output_path)

    # Generate summary statistics
    valid_predictions = [p for p in predictions if p is not None]
    summary = {}
    if valid_predictions:
        summary = {
            "mean": np.mean(valid_predictions),
            "std": np.std(valid_predictions),
            "min": np.min(valid_predictions),
            "max": np.max(valid_predictions)
        }

    return {
        "result": predictions,
        "summary": summary,
        "output_file": str(output_path) if output_path else None,
        "metadata": {
            "mode": "batch",
            "input_file": str(input_file),
            "num_peptides": len(data),
            "num_valid_predictions": len(valid_predictions),
            "config": config
        }
    }

# ==============================================================================
# CLI Interface
# ==============================================================================
def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--input', '-i', help='Input CSV file with peptide data')
    parser.add_argument('--output', '-o', default='predictions.csv', help='Output CSV file for predictions (default: predictions.csv)')
    parser.add_argument('--smiles', '-s', help='Single SMILES string to predict')
    parser.add_argument('--sequence', help='Amino acid sequence for single prediction')
    parser.add_argument('--config', '-c', help='Config file (JSON)')
    parser.add_argument('--device', default='cpu', choices=['cpu', 'cuda'], help='Device to run inference on (default: cpu)')

    args = parser.parse_args()

    # Validate arguments
    if not args.input and not args.smiles:
        print("Error: Either --input file or --smiles must be provided")
        return 1

    # Load config if provided
    config = None
    if args.config:
        with open(args.config) as f:
            config = json.load(f)

    # Add CLI args to config
    if config is None:
        config = {}
    config["device"] = args.device

    try:
        # Run prediction
        result = run_predict_membrane_permeability(
            input_file=args.input,
            output_file=args.output if args.input else None,
            smiles=args.smiles,
            sequence=args.sequence,
            config=config
        )

        if args.smiles:
            # Single prediction output
            if result["result"] is not None:
                print(f"Predicted PAMPA value: {result['result']:.4f}")
                print("Note: Negative values indicate low membrane permeability")
            else:
                print("Error: Could not process the provided SMILES")
        else:
            # Batch prediction output
            print(f"Predictions saved to: {result['output_file']}")

            if result["summary"]:
                print(f"\nPrediction Summary:")
                print(f"  Mean PAMPA: {result['summary']['mean']:.4f}")
                print(f"  Std PAMPA:  {result['summary']['std']:.4f}")
                print(f"  Min PAMPA:  {result['summary']['min']:.4f}")
                print(f"  Max PAMPA:  {result['summary']['max']:.4f}")
                print("Note: Negative values indicate low membrane permeability")

        return 0

    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == '__main__':
    exit(main())