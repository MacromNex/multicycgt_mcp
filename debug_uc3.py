#!/usr/bin/env python3
"""Debug script for UC-003 data size mismatch issue"""

import pandas as pd
import numpy as np

# Load the data
data = pd.read_csv('examples/data/sample_small.csv')
print("Original data shape:", data.shape)
print("Columns:", data.columns.tolist())
print("\nFirst few rows of relevant columns:")
print(data[['MolWt', 'PAMPA']].head())

print("\nMolWt info:")
print("Count:", data['MolWt'].count())
print("NaN count:", data['MolWt'].isna().sum())

print("\nPAMPA info:")
print("Count:", data['PAMPA'].count())
print("NaN count:", data['PAMPA'].isna().sum())
print("Min:", data['PAMPA'].min())
print("Max:", data['PAMPA'].max())

# Try to replicate the pd.cut operation
try:
    permeability_cat = pd.cut(
        data['PAMPA'],
        bins=[-np.inf, -5, -4, -3, np.inf],
        labels=['Low', 'Medium-Low', 'Medium-High', 'High']
    )
    print("\nPermeability categories:")
    print("Count:", permeability_cat.count())
    print("NaN count:", permeability_cat.isna().sum())
    print("Value counts:\n", permeability_cat.value_counts())
except Exception as e:
    print("Error in pd.cut:", e)

# Check for any data filtering that might cause size mismatch
print("\nData types:")
print("MolWt dtype:", data['MolWt'].dtype)
print("PAMPA dtype:", data['PAMPA'].dtype)