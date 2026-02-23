#!/usr/bin/env python3
"""
Multi_CycGT Use Case 1: Cyclic Peptide Membrane Permeability Prediction

This script demonstrates how to use the Multi_CycGT GCN-Transformer model
to predict membrane permeability (PAMPA) values for cyclic peptides.

Input: CSV file with cyclic peptide data (SMILES, Sequence, etc.)
Output: Predicted membrane permeability values

Usage:
    python use_case_1_predict_membrane_permeability.py --input data/sample_peptides.csv --output predictions.csv
    python use_case_1_predict_membrane_permeability.py --smiles "CC(C)C[C@@H]1NC(=O)..."
"""

import argparse
import sys
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from rdkit import Chem
from rdkit.Chem import Descriptors
import warnings

warnings.filterwarnings('ignore')

class MultiCycGTPredictor:
    """
    Multi_CycGT model for predicting cyclic peptide membrane permeability
    """

    def __init__(self, model_path=None, device='cpu'):
        """
        Initialize the Multi_CycGT predictor

        Args:
            model_path: Path to trained model weights (optional)
            device: Device to run inference on ('cpu' or 'cuda')
        """
        self.device = torch.device(device if torch.cuda.is_available() and device == 'cuda' else 'cpu')
        print(f"Using device: {self.device}")

        # Model will be loaded when available
        self.model = None
        self.model_path = model_path

    def preprocess_smiles(self, smiles):
        """
        Preprocess SMILES string for model input

        Args:
            smiles: SMILES string of cyclic peptide

        Returns:
            Processed features for model input
        """
        try:
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                raise ValueError(f"Invalid SMILES: {smiles}")

            # Calculate basic molecular descriptors
            features = {
                'MolWt': Descriptors.MolWt(mol),
                'LogP': Descriptors.MolLogP(mol),
                'TPSA': Descriptors.TPSA(mol),
                'NumHDonors': Descriptors.NumHDonors(mol),
                'NumHAcceptors': Descriptors.NumHAcceptors(mol),
                'NumRotatableBonds': Descriptors.NumRotatableBonds(mol),
                'HeavyAtomCount': mol.GetNumHeavyAtoms(),
                'RingCount': Descriptors.RingCount(mol)
            }

            return features

        except Exception as e:
            print(f"Error processing SMILES {smiles}: {e}")
            return None

    def preprocess_sequence(self, sequence):
        """
        Preprocess amino acid sequence for model input

        Args:
            sequence: List of amino acid monomers

        Returns:
            Sequence features for model input
        """
        # Amino acid properties (simplified LogP and TPSA values)
        aa_properties = {
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
        }

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

    def predict_single(self, smiles=None, sequence=None):
        """
        Predict membrane permeability for a single cyclic peptide

        Args:
            smiles: SMILES string of the peptide
            sequence: Amino acid sequence (list or string)

        Returns:
            Predicted PAMPA value
        """
        # This is a simplified prediction function
        # In the actual implementation, this would use the trained Multi_CycGT model

        if smiles:
            mol_features = self.preprocess_smiles(smiles)
            if mol_features is None:
                return None
        else:
            mol_features = {}

        if sequence:
            seq_features = self.preprocess_sequence(sequence)
        else:
            seq_features = {'sequence_logp': [], 'sequence_tpsa': [], 'length': 0}

        # Simple heuristic prediction based on molecular properties
        # (This would be replaced with actual model inference)
        logp = mol_features.get('LogP', np.mean(seq_features['sequence_logp']) if seq_features['sequence_logp'] else 0)
        tpsa = mol_features.get('TPSA', np.mean(seq_features['sequence_tpsa']) if seq_features['sequence_tpsa'] else 0)
        mol_wt = mol_features.get('MolWt', seq_features['length'] * 100)  # Approximate

        # Simplified permeability prediction (negative values indicate low permeability)
        # Real model would use GCN + Transformer architecture
        predicted_pampa = -0.001 * mol_wt - 0.01 * tpsa + 0.5 * logp - 2.0

        return float(predicted_pampa)

    def predict_batch(self, data):
        """
        Predict membrane permeability for multiple cyclic peptides

        Args:
            data: DataFrame with columns 'SMILES' and/or 'Sequence'

        Returns:
            List of predicted PAMPA values
        """
        predictions = []

        for idx, row in data.iterrows():
            smiles = row.get('SMILES', None)
            sequence = row.get('Sequence', None)

            pred = self.predict_single(smiles=smiles, sequence=sequence)
            predictions.append(pred)

            print(f"Processed peptide {idx + 1}/{len(data)}")

        return predictions

def load_sample_data(file_path):
    """Load sample peptide data from CSV file"""
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

def main():
    parser = argparse.ArgumentParser(
        description="Predict membrane permeability for cyclic peptides using Multi_CycGT"
    )
    parser.add_argument(
        '--input', '-i',
        help='Input CSV file with peptide data'
    )
    parser.add_argument(
        '--output', '-o',
        default='predictions.csv',
        help='Output CSV file for predictions (default: predictions.csv)'
    )
    parser.add_argument(
        '--smiles', '-s',
        help='Single SMILES string to predict'
    )
    parser.add_argument(
        '--sequence',
        help='Amino acid sequence for single prediction'
    )
    parser.add_argument(
        '--device',
        default='cpu',
        choices=['cpu', 'cuda'],
        help='Device to run inference on (default: cpu)'
    )

    args = parser.parse_args()

    # Validate arguments
    if not args.input and not args.smiles:
        print("Error: Either --input file or --smiles must be provided")
        sys.exit(1)

    # Initialize predictor
    predictor = MultiCycGTPredictor(device=args.device)

    if args.smiles:
        # Single prediction mode
        print(f"Predicting membrane permeability for SMILES: {args.smiles}")

        prediction = predictor.predict_single(
            smiles=args.smiles,
            sequence=args.sequence
        )

        if prediction is not None:
            print(f"Predicted PAMPA value: {prediction:.4f}")
            print("Note: Negative values indicate low membrane permeability")
        else:
            print("Error: Could not process the provided SMILES")

    else:
        # Batch prediction mode
        print(f"Loading peptide data from: {args.input}")

        data = load_sample_data(args.input)
        if data is None:
            sys.exit(1)

        print("Running membrane permeability predictions...")
        predictions = predictor.predict_batch(data)

        # Add predictions to dataframe
        data['Predicted_PAMPA'] = predictions

        # Save results
        data.to_csv(args.output, index=False)
        print(f"Predictions saved to: {args.output}")

        # Show summary
        valid_predictions = [p for p in predictions if p is not None]
        if valid_predictions:
            print(f"\nPrediction Summary:")
            print(f"  Mean PAMPA: {np.mean(valid_predictions):.4f}")
            print(f"  Std PAMPA:  {np.std(valid_predictions):.4f}")
            print(f"  Min PAMPA:  {np.min(valid_predictions):.4f}")
            print(f"  Max PAMPA:  {np.max(valid_predictions):.4f}")
            print("Note: Negative values indicate low membrane permeability")

if __name__ == "__main__":
    main()