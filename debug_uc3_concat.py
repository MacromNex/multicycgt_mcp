#!/usr/bin/env python3
"""Debug script for UC-003 data concatenation issue"""

import sys
import pandas as pd
import numpy as np
from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors
import warnings
warnings.filterwarnings('ignore')

class CyclicPeptideAnalyzer:
    def calculate_molecular_properties(self, smiles_list):
        properties = []
        property_names = ['MolWt', 'MolLogP', 'TPSA', 'NumHDonors', 'NumHAcceptors',
                         'NumRotatableBonds', 'HeavyAtomCount', 'RingCount']

        for i, smiles in enumerate(smiles_list):
            try:
                mol = Chem.MolFromSmiles(smiles)
                if mol is None:
                    properties.append({prop: np.nan for prop in property_names})
                    print(f"Warning: Failed to parse SMILES {i}: {smiles[:50]}...")
                    continue

                prop_dict = {
                    'MolWt': Descriptors.MolWt(mol),
                    'MolLogP': Descriptors.MolLogP(mol),
                    'TPSA': Descriptors.TPSA(mol),
                    'NumHDonors': Descriptors.NumHDonors(mol),
                    'NumHAcceptors': Descriptors.NumHAcceptors(mol),
                    'NumRotatableBonds': Descriptors.NumRotatableBonds(mol),
                    'HeavyAtomCount': mol.GetNumHeavyAtoms(),
                    'RingCount': Descriptors.RingCount(mol)
                }
                properties.append(prop_dict)

            except Exception as e:
                print(f"Error processing SMILES {i}: {e}")
                properties.append({prop: np.nan for prop in property_names})

        df = pd.DataFrame(properties)
        print(f"Molecular properties calculated for {len(df)} molecules")
        return df

    def analyze_sequence_properties(self, data):
        # Just return empty for this debug
        return pd.DataFrame()

# Load the data
data = pd.read_csv('examples/data/sample_small.csv')
print("Original data shape:", data.shape)
print("Original data columns with 'Mol':", [c for c in data.columns if 'Mol' in c])

analyzer = CyclicPeptideAnalyzer()

# Calculate molecular properties
mol_properties = analyzer.calculate_molecular_properties(data['SMILES'].tolist())
print("Molecular properties shape:", mol_properties.shape)
print("Molecular properties columns:", mol_properties.columns.tolist())

# Check for column overlap
overlap_cols = set(data.columns) & set(mol_properties.columns)
print("Overlapping columns:", overlap_cols)

# Check if there are any duplicate MolWt columns causing the issue
print("\nData MolWt sample:", data['MolWt'].iloc[:3].values)
print("Calculated MolWt sample:", mol_properties['MolWt'].iloc[:3].values)

# Try concatenation
try:
    seq_properties = analyzer.analyze_sequence_properties(data)
    combined_data = pd.concat([data, mol_properties, seq_properties], axis=1)
    print("Combined data shape:", combined_data.shape)

    # Check MolWt in combined data
    molwt_cols = [c for c in combined_data.columns if c == 'MolWt']
    print("MolWt columns in combined data:", molwt_cols)
    print("Number of MolWt columns:", len(molwt_cols))

    if len(molwt_cols) > 1:
        print("Multiple MolWt columns detected!")
        # Check the values in each
        for i, col in enumerate(molwt_cols):
            print(f"MolWt column {i} first 3 values:", combined_data[col].iloc[:3].values)

except Exception as e:
    print("Error during concatenation:", e)